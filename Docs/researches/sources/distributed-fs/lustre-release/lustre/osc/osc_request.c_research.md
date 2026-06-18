# Research: sources/distributed-fs/lustre-release/lustre/osc/osc_request.c

## Purpose
`osc_request.c` is the main Lustre Object Storage Client request implementation. It translates OBD/OSC operations into OST PTLRPCs, manages asynchronous read/write BRW RPC construction and completion, integrates with LDLM locks, tracks OST grant accounting, handles checksums and encryption bounce pages, exposes statfs/getinfo/setinfo/iocontrol operations, and registers the OSC OBD type at module init.

## Important APIs, Types, And Functions
The file defines small async argument structures for setattr, fsync, ladvise, and BRW/grant use. Externally visible entry points include `osc_setattr_async()`, `osc_ladvise_base()`, `osc_punch_send()`, `osc_fallocate_base()`, `osc_sync_base()`, `osc_shrink_grant_to_target()`, `osc_schedule_grant_work()`, `osc_init_grant()`, `osc_build_rpc()`, `osc_send_empty_rpc()`, `osc_enqueue_base()`, `osc_match_base()`, `osc_set_info_async()`, `osc_reconnect()`, `osc_disconnect()`, `osc_ldlm_resource_invalidate()`, `osc_setup_common()`, `osc_setup()`, `osc_precleanup_common()`, and `osc_cleanup_common()`.

The central request helper is `osc_pack_req_body()`, which writes a wire `obdo` into `RMF_OST_BODY` and stores the project ID in the Lustre message. The central data path is `osc_build_rpc()` -> `osc_brw_prep_request()` -> PTLRPC send -> `brw_interpret()` -> `osc_brw_fini_request()`.

## Control Flow
Simple metadata/object operations allocate a PTLRPC request for a specific OST opcode, pack the request capsule, copy `obdo` fields, size the reply, send synchronously with `ptlrpc_queue_wait()` or asynchronously through a request set/`ptlrpcd`, and unpack `RMF_OST_BODY`. This pattern appears in getattr, setattr, create, punch, fallocate, sync, statfs, getinfo, and setinfo paths.

Destroy first gathers local LDLM locks for early cancellation with `osc_resource_get_unused()`, prepares an ELC destroy request, throttles the number of destroy RPCs through `cl_destroy_in_flight`, and sends it asynchronously. The destroy interpreter decrements the in-flight count and wakes waiters.

Grant flow is woven through all write and maintenance paths. `osc_announce_cached()` adds dirty/undirty/grant/lost-grant state to outgoing `obdo`s. `osc_update_grant()` consumes server returned grant. A delayed global work item walks `client_gtd.gtd_clients`, calls `osc_should_shrink_grant()`, and sends shrink requests in batches. `osc_init_grant()` initializes grant values from connect data and adjusts max pages per RPC to grant chunk alignment when `GRANT_PARAM` is negotiated.

For BRW RPCs, `osc_build_rpc()` receives a list of extents in `OES_RPC`, counts pages and grants, performs unaligned DIO copies, allocates the page pointer array and `obdo`, fills request attributes, sorts pages by object offset, calls `osc_brw_prep_request()`, attaches commit and interpret callbacks, moves pages and extents into async args, updates in-flight counters and histograms, and queues the request to `ptlrpcd`.

`osc_brw_prep_request()` chooses `OST_READ` or `OST_WRITE`, uses a request pool for writes when possible, handles encrypted writes by replacing plaintext folios with encrypted bounce folios, expands encrypted read ranges to encryption units, merges contiguous compatible pages into niobufs, chooses short I/O when small enough and supported, otherwise attaches a passive bulk descriptor, fills `obd_ioobj` and `niobuf_remote`, announces cached grant, optionally marks recovery resend and grant shrink, computes checksums for writes, requests checksums for reads, and stores all completion metadata in `osc_brw_async_args`.

`osc_brw_fini_request()` validates the OST reply, updates quota state from write replies, updates grant, unwraps protected bulk, verifies write checksums and per-niobuf return codes, copies short-read data, zero-fills short reads, verifies read checksums, decrypts encrypted read data when a key exists, and copies returned `obdo` attributes back to the caller's `obdo` on success. Recoverable checksum/security/server-progress errors return `-EAGAIN` or `-EINPROGRESS` for higher-level retry.

`brw_interpret()` restores bounce-page metadata, handles recoverable resend via `osc_brw_redo_request()`, updates object attributes and KMS/size on success, marks unstable write pages for sync, processes async writeback error state, finishes all extents, updates transferred counters and latency histograms, decrements in-flight counters, wakes cache waiters, and unplugs more OSC I/O.

LDLM integration starts by page-aligning extent policies. `osc_enqueue_base()` first tries to match an existing local lock; if none suffices, it packs and sends an LDLM enqueue, with async completion through `osc_enqueue_interpret()`. `osc_match_base()` performs local lock matching and updates cached LVB state. Import events clean grants, notify observers, invalidate LDLM resources and OSC objects, and initialize grant from OCD data.

## State And Persistence
Persistent storage updates are remote on OSTs; this file manages volatile client state. Important state includes request pool sizing (`osc_rq_pool`, `osc_pool_req_count`), in-flight read/write/direct counters, dirty/grant/reserved/lost-grant counters, async error forcing in `osc_async_rc`, delayed grant-shrink client lists, shrinker registration, lock AST data pointing to OSC objects, replayable PTLRPC request state, and request histograms.

The BRW path temporarily mutates `brw_page` offsets/counts for encryption-unit alignment and bounce folios. `osc_release_bounce_pages()` must restore those fields before completion propagates. Write persistence is observed through PTLRPC commit callbacks: `brw_commit()` decrements unstable pages when the server commits, or marks the request committed if the callback races before unstable accounting is set.

## Dependencies And Integration Points
This file is tightly coupled to PTLRPC (`ptlrpc_request_*`, `ptlrpcd_add_req()`, request sets, bulk descriptors), LDLM (`ldlm_*` lock matching/enqueue/cancel), CL/OSC object and extent layers (`cl_req_attr_set()`, `osc_extent_finish()`, `osc_io_unplug()`), quota code (`osc_quota_setdq()` and `osc_quotactl()`), llcrypt/Lustre encryption helpers, checksum helpers, lprocfs histograms, import recovery events, and kernel shrinker/debugfs/module registration.

The `osc_obd_ops` table is the public integration point for the OBD class. Module init allocates the shrinker, request pool, and grant work machinery before registering the `LUSTRE_OSC_NAME` type; exit reverses those resources.

## Risks
The BRW path has high concurrency and ownership complexity. Page arrays, extents, async args, request references, bounce pages, bulk descriptors, and unstable-page accounting must transfer exactly once across normal completion and resend. Error paths before queuing must finish extents and free `oa`/page arrays without touching request-owned resources. Checksum retry can mask transport corruption but can also create repeated resend pressure. Encrypted direct I/O temporarily edits folio mapping/index and depends on careful restoration.

Grant accounting is intentionally approximate under races, but underflow or stale lost-grant handling can affect write throttling. LDLM lock data attachment can fail if a matched lock already belongs to another OSC object. Import invalidation traverses namespace resources without taking references until it finds AST data, so callback and cleanup ordering are sensitive.

## Test Signals
Existing fail hooks named in the file are strong test anchors: `OBD_FAIL_OSC_BRW_PREP_REQ`, `OBD_FAIL_OSC_BRW_PREP_REQ2`, checksum send/receive corruption, `OBD_FAIL_OSC_MARK_COMPRESSED`, `OBD_FAIL_OSC_DELAY_IO`, LDLM enqueue/cancel race hooks, `OBD_FAIL_OSC_MATCH`, and `OBD_FAIL_OSC_SHUTDOWN`. Behavioral tests should cover short I/O reads/writes, encrypted buffered and direct I/O, checksum retry and dump behavior, grant shrink/reconnect, quota flag propagation, BRW resend after `-EINPROGRESS`, lock match/enqueue paths, statfs cache vs remote fetch, and setup/cleanup under connect/disconnect races.
