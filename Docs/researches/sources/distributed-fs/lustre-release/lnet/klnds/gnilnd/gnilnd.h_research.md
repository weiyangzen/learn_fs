# sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd.h

## Purpose

`gnilnd.h` is the central private interface for the gnilnd driver. It defines compile-time constants, wire protocol structures, runtime tunables, all major runtime state structures, refcount/list transition helpers, debug helpers, scheduling macros, lookup helpers, public prototypes for sibling implementation files, and the inclusion point for GNI API wrappers plus Gemini/Aries platform headers.

## Important APIs, Types, And Definitions

- Protocol constants: `GNILND_MSG_VERSION`, `GNILND_CONNREQ_VERSION`, `GNILND_MSG_*`, `GNILND_CONNREQ_*`, `GNILND_DGRAM_*`, connection/peer/quiesce/delete/reverse-RDMA states.
- Wire structures: `kgn_connreq_t`, `kgn_gniparams_t`, `kgn_msg_t`, `kgn_rdma_desc_t`, immediate/PUT/GET/completion message payload structs. These are `__packed` and form the GNI/LNet on-wire contract.
- Runtime types: `kgn_tunables_t`, `kgn_device_t`, `kgn_net_t`, `kgn_dgram_t`, `kgn_tx_t`, `kgn_conn_t`, `kgn_peer_t`, `kgn_rx_t`, `kgn_data_t`.
- ID helpers: `kgn_tx_ev_id_t`, `kgnilnd_cqid2connlist()`, `kgnilnd_cqid2conn_locked()`, `kgnilnd_get_cqid_locked()`, `kgnilnd_validate_tx_ev_id()`.
- Locking and allocation helpers: `kgnilnd_gl_mutex_lock()`, `kgnilnd_conn_mutex_lock()`, `kgnilnd_trylock()`, `kgnilnd_vzalloc()`, `kgnilnd_vfree()`.
- Refcount helpers: `kgnilnd_net_addref/decref`, `kgnilnd_peer_addref/decref`, `kgnilnd_conn_addref/decref`, `kgnilnd_admin_addref/decref`.
- TX state helpers: `kgnilnd_tx_state2list()`, `kgnilnd_tx_add_state_locked()`, `kgnilnd_tx_del_state_locked()`, `kgnilnd_tx_mapped()`.
- Lookup and policy helpers: `kgnilnd_find_net()`, `kgnilnd_can_unlink_peer_locked()`, `kgnilnd_conn_clean_errno()`, `kgnilnd_check_purgatory_errno()`, `kgnilnd_check_purgatory_conn()`.
- Debug/string helpers: `GNIDBG_MSG`, `GNIDBG_CONN`, `GNIDBG_TX`, `GNITX_ASSERTF`, and enum-to-string functions near the end of the file.

## Control Flow

This header does not own an independent runtime control loop, but it encodes the control-flow contracts used by the implementation. TX descriptors move from `GNILND_TX_ALLOCD` to peer, map, FMA, RDMA, live, dying, and freed states through inline helpers that also update list membership, connection/peer refs, and device counters. Connection destruction is partly encoded in `kgnilnd_conn_decref()`: when the refcount drops to one while an endpoint still exists, it changes state to `GNILND_CONN_DESTROY_EP` and schedules the connection; when the refcount reaches zero it calls `kgnilnd_destroy_conn()`.

The header also drives build-time platform selection. It includes `gnilnd_hss_ops.h`, then `gnilnd_api_wrap.h`, then either `gnilnd_gemini.h` or `gnilnd_aries.h` based on hardware configuration. `kgnilnd_check_kgni_version()` uses `symbol_get(kgni_driver_version)` and the selected platform's `GNILND_KGNI_TS_MINOR_VER` to decide whether to use thread-safe KGNI calls or global locking.

## State And Persistence Behavior

All state is in memory and scoped to the loaded kernel module. `kgn_data_t` is the authoritative global state container; `kgn_device_t`, `kgn_net_t`, `kgn_peer_t`, `kgn_conn_t`, `kgn_tx_t`, and `kgn_dgram_t` are the main state-bearing objects. The header makes list membership a state invariant: peers live in hash lists, connections live in peer and CQ hash lists until closing, TX descriptors carry both a list state and a `tx_list_p` pointer, and MDD/mailbox purgatory state is explicit. Tunables are pointer fields in `kgn_tunables_t`, so most macros read current module tunable values dynamically.

## Dependencies And Integration Points

The header depends on Linux kernel primitives, libcfs fail/debug infrastructure, LNet private headers, and Cray `gni_pub.h`. It provides the shared contract for all files in `lnet/klnds/gnilnd`, including startup/shutdown, datagram, transmit, receive, scheduler, reaper, FMA memory, sysctl/proc, quiesce/reset, and hardware translation modules. Its packed wire structs integrate directly with remote gnilnd peers and therefore with the protocol compatibility story.

## Risks And Edge Cases

- Wire structure changes require protocol version discipline. The comments explicitly warn that early `kgn_connreq_t` fields cannot move without breaking NAK behavior.
- `kgn_tx_ev_id_t` uses bitfields inside unions for CQID/TX-index extraction. This is fast but layout-sensitive and should be treated carefully across compiler/architecture changes.
- Refcount macros have side effects and call destroy/schedule functions. Any change to the ownership model can create use-after-free, leaked endpoint refs, or scheduler recursion.
- TX list helpers assume callers hold the appropriate TX, conn, peer, or device locks. They intentionally LBUG on inconsistent state.
- `kgnilnd_conn_decref()` relies on subtle connection close invariants documented in the long safety comment; this is a major concurrency hotspot.
- `kgnilnd_check_purgatory_conn()` suppresses purgatory for loopback and clean shutdown errors; changes to error classification can affect mailbox reuse safety.
- `kgnilnd_find_net()` uses `down_read_trylock()` and returns `-ESHUTDOWN` on contention, so callers must distinguish shutdown/lookup failure from normal absence.

## Test Signals

Build tests should cover both `CONFIG_CRAY_GEMINI` and `CONFIG_CRAY_ARIES` selection, compute/service variants, thread-safe and global-lock KGNI versions, and debug builds where enum-to-string switch coverage can catch missing states. Runtime tests should watch refcount counters, list assertions, TX state transitions, CQID validation, purgatory decisions, and fail-injected close/reset/shutdown paths.
