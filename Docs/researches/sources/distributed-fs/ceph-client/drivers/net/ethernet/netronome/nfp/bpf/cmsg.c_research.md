<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/cmsg.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/cmsg.c

## Purpose
This file implements BPF app control-message operations over the common NFP control channel. It allocates/free firmware map tables, performs map lookup/update/delete/get-first/get-next operations, manages a short-lived multi-entry map cache, computes control-message MTU requirements, and dispatches firmware-originated BPF events.

## Important APIs, Types, And Functions
- Map lifecycle: `nfp_bpf_ctrl_alloc_map()` sends `NFP_CCM_TYPE_BPF_MAP_ALLOC` and returns a firmware table id; `nfp_bpf_ctrl_free_map()` sends `NFP_CCM_TYPE_BPF_MAP_FREE` and logs leak risks on failure.
- Entry operations: `nfp_bpf_ctrl_update_entry()`, `nfp_bpf_ctrl_del_entry()`, `nfp_bpf_ctrl_lookup_entry()`, `nfp_bpf_ctrl_getfirst_entry()`, and `nfp_bpf_ctrl_getnext_entry()` all use `nfp_bpf_ctrl_entry_op()`.
- Cache helpers: `nfp_bpf_ctrl_op_cache_get()` handles lookup/getnext hits and invalidation blockers; `nfp_bpf_ctrl_op_cache_put()` installs or releases cached replies with generation checks.
- Message sizing: `nfp_bpf_cmsg_map_req_size()`, `nfp_bpf_cmsg_map_reply_size()`, `nfp_bpf_ctrl_cmsg_min_mtu()`, `nfp_bpf_ctrl_cmsg_mtu()`, and `nfp_bpf_ctrl_cmsg_cache_cnt()`.
- Receive path: `nfp_bpf_ctrl_msg_rx()` handles skb control messages, while `nfp_bpf_ctrl_msg_rx_raw()` accepts raw event buffers.

## Control Flow
Requests allocate a control skb sized for the fixed header plus key/value arrays, fill big-endian firmware fields, and call `nfp_ccm_communicate()` with the corresponding `enum nfp_ccm_type`. Allocation replies are fixed-size and include a table id. Entry replies are variable-size, so `nfp_bpf_ctrl_entry_op()` validates minimum length, firmware status, reply count, and final expected length before copying returned key/value bytes.

The map cache is intentionally tiny and time-bound. Lookup and getnext can satisfy from an skb cached by getfirst/getnext. Update and delete increment `cache_blockers` before issuing firmware I/O, then invalidate by bumping `cache_gen` on completion. Fill operations install the reply only if no blocker ran and the generation still matches. Firmware BPF event messages bypass CCM reply matching and are forwarded to `nfp_bpf_event_output()`.

## State And Persistence
State is in memory only. `struct nfp_bpf_map` owns cache fields (`cache`, `cache_to`, `cache_gen`, `cache_blockers`) protected by `cache_lock`. Firmware persists map contents in device-managed tables identified by `tid`; the driver mirrors only table ids and caches short-lived replies. No filesystem persistence exists.

## Dependencies And Integration Points
The file depends on `ccm.h` for request/reply transport, `fw.h` for BPF control-message ABIs, `main.h` for BPF app/map state, Linux skb/timekeeping/bitops APIs, and `nfp_app_ctrl_msg_alloc()`/`nfp_ccm_communicate()` for transport. It is called by BPF map device ops in `offload.c` and by the app control-message receive hooks in `main.c`.

## Risks And Edge Cases
- ABI v2 uses fixed 64-byte key/value slots; ABI v3 uses firmware-reported max key/value sizes, so MTU sizing must match parsed capabilities.
- `flags` are truncated to firmware's 32-bit field and rejected if high bits are set.
- Multi-entry cache correctness relies on blocker/generation ordering around concurrent update/delete and lookup/getnext operations.
- Variable-length replies must be exact; short or overlong replies are treated as I/O errors.
- `nfp_bpf_ctrl_free_map()` can only warn on allocation/I/O errors, because firmware map leaks may be unrecoverable after host state is gone.

## Test Signals
Test map allocation/free for supported and unsupported map shapes, update/delete invalidating lookup/getnext cache, getfirst/getnext multi-entry replies with ABI v3 MTU sizing, firmware error-code translation to Linux errno, malformed or short control replies, BPF event delivery, and cleanup with no cached skb leaks or cache blocker warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/bpf/cmsg.c -->
