# Research: subset-b-007641

Grouped research for the gnilnd core/header/API wrapper/Aries platform headers. Each section preserves the source path and is bounded for reconciliation into the source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd.c -->
# sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd.c

## Purpose

`gnilnd.c` is the core module and lifecycle implementation for Lustre's Cray GNI LNet network driver. It registers `the_kgnilnd` with LNet, owns the global `kgnilnd_data` runtime object, creates and tears down GNI devices, nets, peers, connections, scheduler/dgram/reaper threads, and handles administrative peer/connection control paths. Message send/receive mechanics live in sibling files, but this file is the control-plane spine that makes those paths possible.

## Important APIs, Types, And Functions

- `the_kgnilnd`: the `struct lnet_lnd` exported to LNet with startup, shutdown, ctl, send, recv, eager recv, tunable, netlink, and timeout hooks.
- `kgnilnd_tun_defaults()`, `kgnilnd_nl_get()`, `kgnilnd_nl_set()`: bridge module tunables into LNet common and netlink-visible settings.
- `kgnilnd_thread_start()` and `kgnilnd_start_sd_threads()`: spawn worker threads and optionally bind scheduler threads to nonzero CPUs.
- Connection lifecycle: `kgnilnd_create_conn()`, `kgnilnd_find_conn_locked()`, `kgnilnd_find_or_create_conn_locked()`, `kgnilnd_destroy_conn_ep()`, `kgnilnd_destroy_conn()`.
- Connection ordering and cleanup: `kgnilnd_conn_isdup_locked()`, `kgnilnd_close_stale_conns_locked()`, `kgnilnd_close_conn_locked()`, `kgnilnd_close_conn()`, `kgnilnd_complete_closed_conn()`.
- Peer lifecycle and admin control: `kgnilnd_create_peer_safe()`, `kgnilnd_add_peer_locked()`, `kgnilnd_add_peer()`, `kgnilnd_del_conn_or_peer()`, `kgnilnd_del_peer_locked()`, `kgnilnd_cancel_peer_connect_locked()`, `kgnilnd_report_node_state()`, `kgnilnd_ctl()`.
- Purgatory handling: `kgnilnd_add_purgatory_locked()`, `kgnilnd_mark_for_detach_purgatory_all_locked()`, `kgnilnd_detach_purgatory_locked()`, `kgnilnd_release_purgatory_list()`.
- Device and module lifecycle: `kgnilnd_dev_init()`, `kgnilnd_dev_fini()`, `kgnilnd_base_startup()`, `kgnilnd_base_shutdown()`, `kgnilnd_startup()`, `kgnilnd_shutdown()`, `kgnilnd_init()`, `kgnilnd_exit()`.

## Control Flow

Module initialization runs via `late_initcall_sync(kgnilnd_init)`. Initialization sets tunables, sysctl/proc entries, `libcfs_setup()`, then registers `the_kgnilnd` with LNet. LNet calls `kgnilnd_startup()` for a network interface; the first interface triggers `kgnilnd_base_startup()`, which zeroes `kgnilnd_data`, initializes lock/list/table/cache state, creates GNI devices and completion queues, allocates FMA mailbox blocks, starts reaper/RCA/ruhroh/scheduler/dgram threads, and posts wildcard datagrams. `kgnilnd_startup()` then allocates a `kgn_net_t`, configures per-NI tunables, selects a GNI device, rewrites the NI address to the GNI device NID, and links the net into the global net hash.

Connection establishment is coordinated through peers and datagrams. `kgnilnd_find_or_create_conn_locked()` returns an established connection when one exists; otherwise it observes reconnect backoff and in-flight endpoint shutdown, marks the peer `GNILND_PEER_CONNECT`, queues it on the device connd list, and wakes datagram processing. `kgnilnd_set_conn_params()` binds the endpoint when needed, sets local/remote event data, initializes SMSG, records peer stamps, and updates timeout/reaper state.

Connection close is staged. `kgnilnd_close_conn_locked()` removes the connection from the CQ hash, marks it closing or closed depending on reset state, optionally puts it in purgatory, resets receive timeout state, and schedules the connection so a CLOSE can be sent. `kgnilnd_complete_closed_conn()` runs after the close message phase, cancels any remaining TX references from `gnc_tx_ref_table`, completes them with the connection error, destroys the endpoint, moves the connection to `GNILND_CONN_DONE`, unlinks it from peer lists when eligible, and notifies LNet. Purgatory is used when a peer may still have stale access to mailbox/MDD resources; the reaper later detaches and releases these resources.

Shutdown mirrors startup but must drain asynchronous state. `kgnilnd_shutdown()` marks the net shutting down, cancels datagrams, deletes peers/connections for that net, wakes quiesced threads if needed, waits for net references, unlinks the net, and calls `kgnilnd_base_shutdown()` when it was the last net. Base shutdown cancels wildcard datagrams, deletes all peers, waits for connections, stops ruhroh and worker threads, unmaps FMA blocks, destroys caches, frees hash tables, finalizes devices, and drops the module reference.

## State And Persistence Behavior

All durable state is in-kernel runtime state; this file writes no persistent on-disk data. The central state object is `kgnilnd_data`, which tracks init/shutdown/reset/quiesce flags, device array, net/peer/connection hash tables, thread counts, cache pointers, connection stamp generators, pending admin counters, and timeout data. LNet interface state is attached through `ni->ni_data` as `kgn_net_t`. Peers and connections are list/refcount managed, with ownership split across peer lists, CQ hash lists, scheduler lists, datagram queues, endpoint references, and TX descriptors. Correctness depends on `kgn_peer_conn_lock`, `kgn_net_rw_sem`, per-device locks, per-connection locks, atomics, and memory barriers such as `set_mb()`.

## Dependencies And Integration Points

The file integrates with LNet through `struct lnet_lnd`, `lnet_register_lnd()`, `lnet_unregister_lnd()`, `lnet_notify()`, NI tunables, and libcfs ioctls. It integrates with Cray GNI through wrapper functions from `gnilnd_api_wrap.h` for CDM, CQ, endpoint, SMSG, memory, error, and quiesce operations. It calls many sibling gnilnd modules through prototypes in `gnilnd.h`: datagram movement, scheduler/reaper/RCA, mailbox/FMA memory handling, transmit/receive logic, sysctl/proc, HSS/RCA node-state translation, and quiesce/reset handling.

## Risks And Edge Cases

- The code is highly sensitive to lock ordering and reference ownership. Many helpers require `kgn_peer_conn_lock` or `kgn_net_rw_sem`; violating those preconditions can create stale peer/connection lookups or premature frees.
- `kgnilnd_base_startup()` reuses loop variable `i` inside the per-device `gnd_dgrams` initialization loop, and `kgnilnd_base_shutdown()` similarly reuses `i` while freeing per-device dgram lists. That pattern can perturb the outer device loop and should be treated as a review hotspot.
- Connection stamp and CQID reuse are central safety boundaries. `kgnilnd_create_conn()` starts `gnc_next_tx` near wrap and asserts `GNILND_MAX_MSG_ID < GNILND_MSGID_CLOSE`, which shows wrap behavior is intentionally stress-prone.
- Purgatory is a correctness mechanism for stale remote mailbox/MDD access. Premature detach or missed `gnp_dirty_eps` accounting could corrupt reused mailbox memory.
- Shutdown paths contain long waits for pending refs, connections, threads, and net references. Missed decrefs can hang module unload or LNet shutdown.
- Loopback handling is special-cased in duplicate/stale connection logic and purgatory checks; it is easy to regress while changing connection-stamp comparisons.

## Test Signals

Useful signals are successful module registration/unregistration, LNet NI startup/shutdown, lctl peer/connection ioctls, peer health notifications, clean unload with zero peers/connections/threads/MDDs, and exercised fail locations from `gnilnd_api_wrap.h` such as CDM/CQ/EP/SMSG/RDMA/memory failures. High-value tests should cover duplicate connection negotiation, stale connection pruning, peer down/up events, admin `del_peer`/`disconnect`/`push`, reset/quiesce shutdown, purgatory release, and `kgn_npending_*` drain behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_api_wrap.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_api_wrap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_aries.h -->
# sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_aries.h

## Purpose

`gnilnd_aries.h` supplies Aries-specific compile-time defaults and the shared-MDD hold buffer helpers required by the generic gnilnd code. It is included only after `gnilnd_hss_ops.h` and `gnilnd_api_wrap.h` through `gnilnd.h` when `CONFIG_CRAY_ARIES` is selected.

## Important APIs And Definitions

- Aries timeout defaults: imports `aries/aries_timeouts_gpl.h` on Cray XT builds, otherwise defines `TIMEOUT_SECS()` and a generic `TO_GNILND_timeout` fallback.
- Hardware policy constants: `GNILND_BASE_TIMEOUT`, `GNILND_CHECKSUM_DEFAULT`, `GNILND_REVERSE_RDMA`, `GNILND_RDMA_DLVR_OPTION`, service-node `GNILND_SCHED_THREADS`, `GNILND_KGNI_TS_MINOR_VER`, and `GNILND_TS_ENABLE`.
- `kgnilnd_register_smdd_buf(kgn_device_t *dev)`: allocates one page, selects `GNI_MEM_READWRITE` plus optional `GNI_MEM_RELAXED_PI_ORDERING`, and registers it with GNI into `dev->gnd_smdd_hold_hndl`.
- `kgnilnd_deregister_smdd_buf(kgn_device_t *dev)`: deregisters the shared-MDD hold memory and frees the page.

## Control Flow

At compile time, the header chooses Aries timeout and reverse-RDMA defaults based on build configuration. At device initialization, `kgnilnd_dev_init()` calls `kgnilnd_register_smdd_buf()` after creating CQs; the helper allocates `dev->gnd_smdd_hold_buf` and calls `kgnilnd_mem_register()`. At device finalization, `kgnilnd_dev_fini()` calls `kgnilnd_deregister_smdd_buf()` when the buffer pointer is set, then clears the pointer after a successful return assertion.

## State And Persistence Behavior

This header adds no global state. It mutates per-device in-memory fields `gnd_smdd_hold_buf` and `gnd_smdd_hold_hndl`. The registered page is a runtime resource used to keep a shared MDD allocated for Aries behavior; it is not persisted across module unload or device reinitialization.

## Dependencies And Integration Points

The file depends on LNet headers, `gnilnd_hss_ops.h` include ordering, Aries timeout headers when available, GNI memory flags, `kgnilnd_tunables.kgn_bte_relaxed_ordering`, and the memory wrappers from `gnilnd_api_wrap.h`. Its constants are consumed by generic gnilnd timeout, scheduler, reverse-RDMA, checksum, and thread-safe KGNI-version logic.

## Risks And Edge Cases

- Include order is enforced with `#error`; direct inclusion without `gnilnd_hss_ops.h` breaks the build.
- Generic-kernel builds rely on the fallback `TO_GNILND_timeout` value, so timeout behavior can differ from Cray XT-provided headers.
- `kgnilnd_register_smdd_buf()` returns a memory-registration error without freeing the allocated page immediately. Current cleanup may recover through device finalization if the pointer remains set, but this is a resource-management hotspot.
- `kgnilnd_deregister_smdd_buf()` frees the page regardless of the deregistration return code. Callers assert success in normal finalization, but error paths should be reviewed carefully.
- Reverse-RDMA defaults differ between compute and service builds, so behavior-sensitive tests need both configurations.

## Test Signals

Build coverage should include Aries compute, Aries service, Cray XT timeout-header, and generic-kernel fallback configurations. Runtime signals include successful shared-MDD buffer allocation/registration during `kgnilnd_dev_init()`, successful deregistration/free during `kgnilnd_dev_fini()`, relaxed-ordering flag propagation when the tunable is set, and correct thread-safe KGNI gating at minor version `0x45`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_aries.h -->
