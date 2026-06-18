# sources/distributed-fs/glusterfs/xlators/nfs/server/src/nlm4.c

## Purpose
Implements the NLMv4 lock manager RPC program used by the GlusterFS NFS server. It handles byte-range lock testing, locking, cancellation, unlocking, share reservations, client cleanup, NSM/statd monitoring, callback RPC clients for granted notifications, service initialization, and statedump reporting.

## Important APIs, Types, and Functions
Service actors include `nlm4svc_null`, `nlm4svc_test`, `nlm4svc_lock`, `nlm4svc_nm_lock`, `nlm4svc_cancel`, `nlm4svc_unlock`, `nlm4svc_share`, `nlm4svc_unshare`, and `nlm4svc_free_all`, registered in `nlm4svc_actors` and exposed by `nlm4svc_init`. `nlm4_init_state` is a stub that currently returns success. `nlm_priv` emits statedump information for active NLM clients and locked file GFIDs.

Request setup helpers include `nlm4_prep_nlm4_testargs`, `nlm4_prep_nlm4_lockargs`, `nlm4_prep_nlm4_cancargs`, `nlm4_prep_nlm4_unlockargs`, `nlm4_prep_shareargs`, and `nlm4_prep_freeallargs`. Reply and conversion helpers include `nlm4svc_submit_reply`, `nlm4_generic_reply`, `nlm4_test_reply`, `nlm4_share_reply`, `nlm4_errno_to_nlm4stat`, `nlm4_lock_to_gf_flock`, `nlm4_gf_flock_to_holder`, `nlm_copy_lkowner`, and `nlm_is_oh_same_lkowner`.

Client and fd tracking is managed by `nlm_add_nlmclnt`, `nlm_get_uniq`, `nlm_get_rpc_clnt`, `nlm_set_rpc_clnt`, `nlm_unset_rpc_clnt`, `nlm_cleanup_fds`, `nlm_search_and_add`, `nlm_search_and_delete`, and `nlm_dec_transit_count`. Share reservations are managed by `nlm4_share_new`, `nlm4_add_share_to_inode`, `nlm4_approve_share_reservation`, `nlm4_create_share_reservation`, `nlm4_remove_share_reservation`, and `nlm4_free_all_shares`. Callback/monitoring paths include `nsm_monitor`, `nlm4_establish_callback`, `nlm_rpcclnt_notify`, `nlm_handle_connect`, `nlm4svc_send_granted`, `nlm4svc_sm_notify`, and `nlm_grace_period_over`.

## Control Flow
NLM requests follow the same general shape as NFSv3 requests: validate the shared NFSv3 state, allocate `nfs3_call_state_t`, decode XDR arguments into `cs->args`, validate the embedded NFSv3 file handle, map it to a child xlator, check grace-period and volume-start state, resolve the file handle, then resume operation-specific logic.

`TEST` resolves the file handle, creates an anonymous fd, converts the NLM lock to `gf_flock`, issues `nfs_lk(..., F_GETLK, ...)`, and replies with granted or denied holder data. `LOCK` resolves and opens a per-client fd keyed by the `nlm_client_t` pointer, tracks the fd in the client's `fdes` list, then issues `F_SETLK` or `F_SETLKW`. Blocking locks first return `nlm4_blocked`; when the lower lock completes, the callback sends an NLM `GRANTED` callback via a cached or newly established RPC client. `CANCEL` and `UNLOCK` find the same client-scoped fd and send an unlock-style `F_SETLK`.

`SHARE` and `UNSHARE` do not issue lower filesystem FOPs. They resolve the file handle and maintain in-memory share reservation lists on the NFS inode context and client object. `FREE_ALL` decodes a caller name and removes both share reservations and tracked fds for that client. `nlm4svc_init` sets up an NLM listener, initializes global lists/locks, restarts rpc.statd/sm-notify state, starts the NSM thread, and starts a timer that clears the NLM grace period.

## State and Persistence Behavior
Global process state includes `nlm_client_list`, `nlm_client_list_lk`, `nlm_grace_period`, and `nlm4_inited`. Each `nlm_client_t` tracks caller address/name, a unique PID-like marker, fd entries, share entries, an optional callback `rpc_clnt`, and whether NSM monitoring has been requested. Each `nlm_fde_t` holds a referenced fd and a transit counter for in-flight lock operations. Each `nlm_share_t` is linked both to a client and to the inode's NFS context share list.

The actual byte-range locks are delegated to lower Gluster locking through `nfs_lk`. Share reservations are memory-only at the NFS xlator layer and are lost on daemon restart. NSM/statd integration provides external recovery signaling: initialization removes notify/statd pid files, kills/restarts rpc.statd, starts an NSM thread, and keeps a grace period during which non-reclaim lock/share requests are denied with `nlm4_denied_grace_period`.

## Dependencies and Integration Points
This file depends on the NFSv3 call-state and file-handle resolver, Gluster FOP wrappers, RPC service/client infrastructure, ONC RPC portmapper calls, NSM XDR, statedump, Gluster run/thread/timer helpers, iobuf/iobref allocation, inode contexts, and lower translator locking support. It is tightly coupled to `nfs3.h` because NLM request arguments, owner bytes, lock file handles, transport references, callback frame references, and resolver state are stored in `nfs3_call_state_t`.

The service is registered as RPC program `100021` version `4` on port `38468`. It also opens outbound client connections to NLM clients to send `GRANTED` callbacks and calls local rpc.statd over TCP for monitoring.

## Risks and Edge Cases
Risk centers on lifetime and concurrency. The global client list protects client/fd/share structures, but callbacks, transit counters, copied frames, callback RPC client notifications, and `GF_REF_*` ownership have many interleavings. Blocking lock behavior must avoid leaking call states or callback frames while still sending exactly one `GRANTED` path. `nlm_client_free` removes fd/share/client lists and may be called from disconnect or FREE_ALL paths, so list ownership must remain consistent.

Protocol risks include grace-period handling, reclaim versus non-reclaim logic, using caller names as client keys, IPv4-only callback setup, portmapper dependency, lock-owner byte copying into fixed Gluster owner buffers, status mapping that collapses many errno values to `nlm4_denied`, and memory-only share reservations that disappear across daemon restart. Operational risk is high in `nlm4svc_init` because it kills/restarts rpc.statd using pid files or `pkill`.

## Test Signals
Useful tests include NFS lock reclaim during and after grace period, `LOCK`/`TEST`/`UNLOCK` success and contention for shared and exclusive byte ranges, blocking lock callback delivery, `CANCEL` for pending blocking locks, `NM_LOCK` without NSM monitoring, statd restart/recovery with `SM_NOTIFY`, client disconnect cleanup, `FREE_ALL` cleanup, share/unshare conflict matrix tests, multi-client caller-name collisions, statedump coverage, and sanitizer/refcount runs over callback connection failures.
