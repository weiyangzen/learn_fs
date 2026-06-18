# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/virt/fdir.c

## Purpose
Implements VF-controlled Flow Director filters over virtchnl. It validates VF requests, starts a VF control VSI for programming completions, parses protocol-header or raw parser-based filter patterns, configures hardware flow profiles, writes add/delete filter descriptors, tracks rule IDs and profile usage, handles asynchronous completion through control VSI Rx descriptors or timeout, and sends virtchnl status responses.

## Important APIs and Functions
- Public entry points: `ice_vc_add_fdir_fltr()`, `ice_vc_del_fdir_fltr()`, `ice_vc_fdir_irq_handler()`, `ice_flush_fdir_ctx()`, `ice_vf_fdir_init()`, and `ice_vf_fdir_exit()`.
- `ice_vc_fdir_param_check()` gates FDIR enablement, VF ACTIVE state, negotiated `VIRTCHNL_VF_OFFLOAD_FDIR_PF`, valid VSI ID, and VF VSI presence.
- Parsing functions include `ice_vc_fdir_parse_pattern()`, `ice_vc_fdir_parse_raw()`, `ice_vc_fdir_parse_action()`, and `ice_vc_validate_fdir_fltr()`.
- Profile functions include `ice_vc_fdir_alloc_prof()`, `ice_vc_fdir_config_input_set()`, `ice_vc_fdir_write_flow_prof()`, `ice_vc_fdir_rem_prof()`, and raw parser profile management in `ice_vc_add_fdir_raw()`/`ice_vc_del_fdir_raw()`.
- Rule bookkeeping uses `idr` plus `fdir_rule_list` through insert/remove/lookup/flush helpers.
- Async completion uses `ice_vc_fdir_set_irq_ctx()`, `ice_vf_fdir_timer()`, `ice_vc_fdir_irq_handler()`, `ice_vf_verify_rx_desc()`, and add/delete post-processing helpers.

## Control Flow
Add flow: check capacity and VF parameters, create/open control VSI if needed, allocate response and config, validate pattern/action, optionally return success for validate-only, configure input set/profile for structured rules or parser profile for raw rules, reject duplicate/conflicting rules, allocate an ID, set a single in-flight IRQ context, write the FDIR programming descriptor through the control VSI, and return only after async completion later sends final status.

Delete flow: validate parameters, look up flow ID, ensure control VSI exists, set in-flight IRQ context, write a delete descriptor, remove unused profile if this was the last structured rule of that flow/tunnel type, and wait for async completion to send final status and remove/free the rule.

Completion flow: control VSI Rx interrupt copies descriptor into `ctx_done`, clears `ctx_irq`, deletes timer, sets `ICE_FD_VF_FLUSH_CTX`, and schedules service. Timer performs the same handoff with timeout status. `ice_flush_fdir_ctx()` iterates VFs under the VF table lock, verifies descriptors, then calls add/delete post handlers to update counters, remove/free failed rules, and send virtchnl responses.

## State and Persistence
Per-VF FDIR state lives in `vf->fdir`: per-flow/tunnel counters, total filter count, dynamic profile array, IDR, rule list, spinlock-protected in-flight/done contexts, and parser/raw profile info in `vf->fdir_prof_info`. The max per-VF filter limit is 128. FDIR state is initialized on VF creation/reset and fully destroyed on VF reset/exit.

## Dependencies and Integration Points
Depends on `ice.h`, `ice_base.h`, `ice_lib.h`, `ice_flow.h`, `ice_vf_lib_private.h`, virtchnl FDIR structs, parser library, flow director hardware APIs, control VSI creation/open, service task scheduling, timers, IDR, spinlocks, and PF/VF reset cleanup. It integrates with allowlisted virtchnl FDIR opcodes and VF lifecycle code that resets FDIR on VF reset.

## Risks
- Only one FDIR operation per VF can be in flight; concurrent add/delete returns `-EBUSY`/no-resource status.
- Several paths allocate with devm and kfree; ownership must remain consistent on validation, async success/failure, and reset.
- Raw parser profile reference counting relies on PTG and field-vector equality; mismatches can leak or prematurely remove profiles.
- Add/delete responses are asynchronous; callers must not assume the immediate function return is the final VF-visible result.
- The structured add post path currently uses `is_tun = 0` for counter updates, while profile setup uses `ice_fdir_is_tunnel(conf->ttype)`; tunnel counter accounting deserves regression coverage.
- Timeout handling depends on service task scheduling to flush `ctx_done`.

## Test Signals
Test invalid VSI/caps/FD disabled cases, validate-only add, duplicate rule detection, profile conflicts between `OTHER` and TCP/UDP/SCTP flows, raw parser filters, max 128 filters, no hardware FDIR space, single in-flight request rejection, add success/failure descriptor verification, delete nonexistent ID, delete last rule removing profile, timeout path, VF reset while FDIR in flight, control VSI creation failure, and cleanup on `ice_vf_fdir_exit()`.
