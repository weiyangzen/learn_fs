# sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_api_wrap.h

## Purpose

`gnilnd_api_wrap.h` wraps Cray GNI API calls in gnilnd-specific inline functions. The wrappers centralize return-code classification, debug logging, fatal escalation for unexpected GNI behavior, and `CFS_FAIL_GNI_*` fault injection points. This keeps the core driver code mostly free of repetitive GNI error-handling switches.

## Important APIs And Definitions

- Failure locations: `CFS_FAIL_GNI_*` values cover physical/virtual mapping, SMSG send/get/release, CDM/CQ/EP operations, datagram probe/post/test, RDMA posting/completion, quiesce, reset races, checksums, timeout paths, purgatory, scheduler deadlines, and CQ errors.
- Return-code helpers: `kgnilnd_api_rc2str()`, `_kgnilnd_api_rc_lbug()`, and macros `GNILND_API_RC_LBUG`, `GNILND_API_SWBUG`, `GNILND_API_EINVAL`, `GNILND_API_RESOURCE`, `GNILND_API_BUSY`.
- CDM/error/quiesce wrappers: `kgnilnd_cdm_create()`, `kgnilnd_cdm_attach()`, `kgnilnd_cdm_destroy()`, `kgnilnd_subscribe_errors()`, `kgnilnd_release_errors()`, `kgnilnd_set_quiesce_callback()`, `kgnilnd_get_quiesce_status()`.
- CQ/SMSG wrappers: `kgnilnd_cq_create()`, `kgnilnd_cq_destroy()`, `kgnilnd_cq_get_event()`, `kgnilnd_smsg_init()`, `kgnilnd_smsg_send()`, `kgnilnd_smsg_getnext()`, `kgnilnd_smsg_release()`.
- Endpoint/datagram wrappers: `kgnilnd_ep_create()`, `kgnilnd_ep_bind()`, `kgnilnd_ep_set_eventdata()`, `kgnilnd_ep_unbind()`, `kgnilnd_ep_destroy()`, `kgnilnd_ep_postdata_w_id()`, `kgnilnd_ep_postdata_test_by_id()`, `kgnilnd_ep_postdata_cancel_by_id()`, `kgnilnd_postdata_probe_by_id()`, `kgnilnd_postdata_probe_wait_by_id()`.
- RDMA/completion/memory wrappers: `kgnilnd_post_rdma()`, `kgnilnd_get_completed()`, `kgnilnd_cq_error_str()`, `kgnilnd_cq_error_recoverable()`, `kgnilnd_mem_register_segments()`, `kgnilnd_mem_register()`, `kgnilnd_mem_deregister()`, `kgnilnd_mem_mdd_release()`.

## Control Flow

Each wrapper follows the same pattern: optionally synthesize a GNI return code from a `CFS_FAIL_CHECK()`, otherwise call the underlying `gni_*` function, then classify the return code. Expected success, retry, timeout, no-match, transaction-error, or resource outcomes are returned to upper layers. Invalid parameter/state outcomes are usually logged as likely software bugs. Unknown or contract-breaking return codes call the LBUG path. Some wrappers intentionally avoid fail injection where fake data could corrupt state, such as `kgnilnd_cq_get_event()` and datagram cancel.

`kgnilnd_get_completed()` first asks KGNI for a real post descriptor and then can inject a transaction error into the returned descriptor. The CQ error-string and recoverability wrappers use the same fail location to synthesize recoverable/fatal transaction details. Memory registration normalizes `GNI_RC_ERROR_NOMEM` to `GNI_RC_ERROR_RESOURCE` because upper layers handle resource failures rather than raw no-memory GNI codes.

## State And Persistence Behavior

The wrapper itself owns no persistent state. It observes global libcfs fail-injection state (`cfs_fail_loc`, `cfs_fail_val`) and caller-provided GNI handles/descriptors. It can mutate output parameters and descriptors, especially during injected datagram termination and injected CQ transaction errors. All effects are in-memory and synchronous with the wrapper call.

## Dependencies And Integration Points

The file depends on `gni_pub.h` types and Cray GNI functions, libcfs debug/fail infrastructure, and gnilnd debug macros. It is included through `gnilnd.h`, so all gnilnd implementation files call these wrappers rather than the raw GNI API. The fail locations are an integration point for Lustre fault-injection tests.

## Risks And Edge Cases

- Unexpected GNI return codes generally LBUG, which is appropriate for strict API contracts but can turn driver/API drift into a kernel crash rather than a degraded error.
- `kgnilnd_cdm_destroy()` checks `CFS_FAIL_GNI_CQ_DESTROY` instead of `CFS_FAIL_GNI_CDM_DESTROY`, leaving the declared CDM-destroy fail point unused and coupling CDM destroy injection to CQ destroy.
- `kgnilnd_smsg_getnext()` checks `CFS_FAIL_GNI_SMSG_RELEASE` even though `CFS_FAIL_GNI_SMSG_GETNEXT` exists, so get-next fault injection may not target the intended call.
- Error injection sometimes runs after real work, for example datagram termination and completion transaction-error injection. Tests using these points must account for real side effects already having occurred.
- Resource failures are deliberately sometimes quiet or debug-level, such as `kgnilnd_post_rdma()` returning `GNI_RC_ERROR_RESOURCE`; callers must implement retry/backoff correctly.
- The `apick_fmt` string for `kgnilnd_mem_register()` appears malformed around the length and pointer formatting, which affects diagnostics rather than behavior.

## Test Signals

Tests should verify that every wrapper returns documented expected codes for success, retry/not-done, no-match, timeout, transaction-error, and resource pressure. Fault-injection coverage should exercise each `CFS_FAIL_GNI_*` location and confirm upper layers respond correctly. Negative tests should validate that invalid parameters log as software bugs and that truly unexpected codes reach the LBUG path in debug environments. Specific regression tests should cover the CDM-destroy and SMSG-getnext fail-location mismatches if those are fixed later.
