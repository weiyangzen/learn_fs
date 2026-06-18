# subset-b-008225 Research

Grouped research for OpenStack Swift object reconstruction, replication, object-server request handling, and ssync sender/receiver protocol files. Each section preserves its source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/obj/reconstructor.py -->
# sources/object-store/openstack-swift/swift/obj/reconstructor.py

## Purpose
Implements the object reconstructor daemon for erasure-coded storage policies. It repairs missing EC fragment archives on primary nodes, synchronizes neighboring EC fragments, reverts handoff fragments to their correct primaries, optionally quarantines stale solitary fragments, and publishes reconstruction progress to recon cache. The module is the EC-policy counterpart to `obj/replicator.py`: it uses suffix hashes and ssync, but must reason about fragment indexes, durable/non-durable EC data, and reconstructing a target fragment from other fragments before sending it.

## Important APIs, Types, And Functions
Top-level helpers include `_get_partners(node_index, part_nodes)`, which selects the left, right, and far primary partners for an EC primary node, and `_full_path(node, part, relative_path, policy)`, which formats remote paths for logs.

`ResponseBucket` groups successful fragment GET responses by backend timestamp. It tracks total responses, useful responses by fragment index, a durable flag, and an EC ETag to reject mixed-fragment sets. `RebuildingECDiskFileStream` adapts reconstructed fragment bytes and metadata to the DiskFile-like interface expected by ssync; it updates `X-Object-Sysmeta-Ec-Frag-Index`, removes old ETag metadata, exposes `content_length`, and yields rebuilt bytes from `reader()`.

`ObjectReconstructor` is the daemon. Its constructor reads operational settings such as devices, Swift dir, ring IP/port, concurrency, `reconstructor_workers`, EC policies, stats/ring intervals, network timeouts, `handoffs_only`, `rebuild_handoff_node_count`, quarantine thresholds, `request_node_count`, and `max_objects_per_revert`. It also configures optional legacy EC CRC behavior via `LIBERASURECODE_WRITE_LEGACY_CRC` and builds a `DiskFileRouter`.

The core repair methods are `_get_response()`, `_handle_fragment_response()`, `_make_fragment_requests()`, `reconstruct_fa()`, `_reconstruct()`, and `make_rebuilt_fragment_iter()`. The partition/suffix workflow is handled by `_get_hashes()`, `get_suffix_delta()`, `_iter_nodes_for_frag()`, `_get_suffixes_to_sync()`, `delete_reverted_objs()`, `process_job()`, `_sync()`, `_revert()`, and `_get_part_jobs()`. Top-level orchestration lives in `get_policy2devices()`, `get_local_devices()`, `collect_parts()`, `build_reconstruction_jobs()`, `reconstruct()`, `run_once()`, and `run_forever()`.

## Control Flow
One reconstruction pass starts in `run_once()` or `run_forever()`, calls `reconstruct()`, resets counters, starts heartbeat and lockup detector greenlets, builds a bounded `GreenPool`, and iterates partition records from `collect_parts()`. `collect_parts()` loads EC rings, skips policies under partition-power increase, selects local ring devices, verifies mounted devices through the DiskFile manager, cleans stale tmp files, creates missing data dirs, validates partition directory names, honors device/partition overrides, and skips primary partitions in `handoffs_only` mode.

For each partition, `build_reconstruction_jobs()` delegates to `_get_part_jobs()`. `_get_part_jobs()` lists/hash suffixes, groups hashes by EC fragment index, determines whether the local node is a primary for the partition, and emits one `SYNC` job for the primary fragment index plus zero or more `REVERT` jobs for fragments that belong elsewhere. Suffixes with only tombstones/metafiles are attached to an existing job when possible; if no fragment hints exist, a sample of primaries is selected so tombstones are not simply lost before another node has seen them.

`SYNC` jobs call `_get_suffixes_to_sync()` for each partner node. That method sends a backend `REPLICATE` request with policy headers, follows eligible handoffs for the same backend index when a primary is unmounted, unpickles remote suffix hashes, computes suffix deltas against the local fragment index and the remote backend index, recalculates local hashes for candidate suffixes, and returns the still-different suffixes. `_sync()` then uses `ssync_sender` with `include_non_durable=False` and the job's `sync_diskfile_builder` callback so missing remote fragments can be rebuilt on demand.

`REVERT` jobs take the replication partition lock, ssync all selected suffixes to their destination primaries with `include_non_durable=True`, track whether `max_objects_per_revert` truncated progress, and call `delete_reverted_objs()` only after all destination nodes succeed. `delete_reverted_objs()` purges the sent fragment index from each local diskfile, handles legacy durable data files by overriding nondurable purge delay, may purge reverted metafiles for pure handoffs, and removes empty suffix directories.

Fragment reconstruction is triggered by ssync sender when the receiver wants data that is not locally the correct fragment for the target node. `reconstruct_fa()` validates the local fragment metadata, calls `_make_fragment_requests()` to GET other fragment archives using `X-Backend-Fragment-Preferences`, and waits for a `ResponseBucket` with at least `policy.ec_ndata` useful fragment indexes at one timestamp and ETag. If enough fragments are available, `make_rebuilt_fragment_iter()` reads one EC fragment-size chunk from each response in lockstep and calls `policy.pyeclib_driver.reconstruct()` to produce the target fragment stream. If only old solitary evidence remains and all other queried nodes say 404, `_is_quarantine_candidate()` may quarantine the local fragment instead of repeatedly trying to rebuild from impossible input.

## State And Persistence
Persistent data lives in Swift object-device directories: partition directories, suffix directories, data/meta/tombstone files, tmp files, EC fragment archive files, and durable markers managed by the DiskFile layer. The reconstructor deletes invalid partition paths, removes empty partitions, purges reverted fragments, removes suffix directories after purge, and can quarantine a fragment through the DiskFile quarantine path. It does not write object bytes directly except through ssync and DiskFile writer paths on remote object servers.

Operational state is kept in daemon counters (`job_count`, `part_count`, `suffix_count`, `suffix_sync`, `suffix_hash`, `handoffs_remaining`, partition timings), `all_local_devices`, ring mtimes, and per-worker logging prefixes. Recon cache updates are written to `RECON_OBJECT_FILE`; in multiprocess mode workers publish per-device `object_reconstruction_per_disk` stats and the parent aggregates them in `aggregate_recon_update()`. The daemon also mutates the process environment for legacy liberasurecode CRC compatibility when configured.

## Dependencies And Integration Points
The module depends on Swift concurrency primitives (`GreenPool`, `GreenPile`, `GreenAsyncPile`, `Timeout`, `tpool`), storage-policy rings (`POLICIES`, `EC_POLICY`), `DiskFileRouter`, EC pyeclib drivers, backend `REPLICATE` and `GET` routes in `obj/server.py`, and `ssync_sender.Sender`. It shares protocol details with `ssync_sender.py` through `sync_diskfile_builder`, `include_non_durable`, and fragment-index headers. It also relies on object-server GET support for `X-Backend-Fragment-Preferences`, durable timestamps, fragment indexes, and backend data timestamps.

Ring and process integration comes from `Daemon`, `run_daemon`, `parse_override_options`, `is_local_device`, recon-cache helpers, and object ring `get_part_nodes()` / `get_more_nodes()`. Backend health and mount status are inferred from HTTP 507 responses, missing device paths, partition locks, and ring-change checks.

## Risks And Edge Cases
The most sensitive behavior is around deletion and quarantine. Handoff fragments are purged only after all intended syncs succeed, but races with incoming SSYNC, ring changes, reclaim age, and `max_objects_per_revert` can leave work for later passes. Quarantine is deliberately strict: only all-404 errors, one local timestamp bucket, age beyond `quarantine_age`, too few useful responses, and the local fragment among useful responses qualify.

Reconstruction correctness depends on grouping responses by timestamp and ETag, validating fragment-index headers, honoring durable timestamps, and reading aligned fragment-size chunks from all sources. Mixed ETags, duplicate fragment indexes, non-durable fragments, unmounted primaries, and duplicated EC fragment policies all have explicit handling but are easy regression areas. Ring changes abort work per policy but jobs already running may still interact with changing placement. `handoffs_only` and legacy `handoffs_first` compatibility are operator-sensitive modes and should not be normal steady state.

## Test Signals
Useful tests would cover `_get_partners()`, suffix-delta comparison across local/remote fragment indexes, `_get_part_jobs()` for primary, handoff, tombstone-only, duplicated EC, and bad fragment-index layouts, `_make_fragment_requests()` bucket selection and quarantine candidate behavior, `make_rebuilt_fragment_iter()` chunk alignment and exception handling, `delete_reverted_objs()` purge decisions, and ring-change/override handling in `collect_parts()`. Integration or probe tests should exercise EC rebuild from missing fragments, non-durable revert flows, handoff-only passes, 507 fallback to handoffs, and ssync callback reconstruction. This local source shard does not include an upstream test tree, so these signals are inferred from the code paths and Swift’s normal unit/probe coverage areas.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/obj/reconstructor.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/obj/replicator.py -->
# sources/object-store/openstack-swift/swift/obj/replicator.py

## Purpose
Implements the object replicator daemon for replicated storage policies. It compares local and remote suffix hashes, transfers out-of-sync suffixes using rsync or ssync, reverts handoff partitions to their primary nodes, removes handoff data after successful sync, and writes replication health statistics to the recon cache. Unlike the EC reconstructor, this daemon handles whole replicated object partitions and does not rebuild fragments.

## Important APIs, Types, And Functions
`DEFAULT_RSYNC_TIMEOUT` defines the default subprocess timeout for rsync. `_do_listdir(partition, replication_cycle)` spreads expensive suffix-directory list operations over ten replication cycles.

`Stats` is the daemon’s recon/stat aggregation type. It tracks attempted jobs, failures, hash matches, removals, rsync/ssync attempts, successful target devices, suffix counts, suffix hashes, suffix syncs, and nested failure counts by remote IP/device. It supports `from_recon()`, `to_recon()`, addition, and `add_failure_stats()`.

`ObjectReplicator` owns configuration, ring/device discovery, transfer methods, job construction, pass execution, and recon updates. Key methods include `get_worker_args()`, `is_healthy()`, `get_local_devices()`, `sync()`, `load_object_ring()`, `_rsync()`, `rsync()`, `ssync()`, `revert()`, `delete_partition()`, `delete_handoff_objs()`, `update()`, `build_replication_jobs()`, `collect_jobs()`, `replicate()`, `update_recon()`, `aggregate_recon_update()`, `run_once()`, and `run_forever()`.

## Control Flow
`run_once()` or `run_forever()` zeroes stats and calls `replicate()`. A replication pass advances `replication_cycle`, starts a heartbeat, collects jobs, checks ring changes, validates device mounts, and dispatches each job into a green pool. Jobs with `delete=True` are handoff reverts; other jobs are primary partition updates.

`collect_jobs()` iterates replication policies, skips policies under `next_part_power`, honors policy overrides, loads rings, and delegates to `build_replication_jobs()`. `build_replication_jobs()` finds local ring devices by IP/port, validates drives through `check_drive()`, cleans stale tmp files, creates missing object data directories, lists partitions, ignores auditor status files, and creates a job containing the partition path, local device, object path, remote primary nodes, delete flag, policy, partition, and local region. A partition becomes a handoff job when the local device is not one of the partition’s primary nodes.

`update()` handles primary partitions. It computes local suffix hashes, shuffles target primary nodes, and chains extra handoff nodes if needed. For each target region not already successfully synced, it sends a backend `REPLICATE` request, handles 507 unmounted responses by trying another node, unpickles remote hashes, computes suffix differences, recalculates local hashes for those suffixes, and invokes the configured `sync_method` (`rsync` by default, `ssync` if configured). Successful cross-region syncs suppress duplicate syncs to the same remote region during the pass.

`revert()` handles handoff partitions under a replication partition lock to avoid cross-replication races with incoming SSYNC. It lists suffix directories, syncs each remote primary, optionally passes `remote_check_objs` for same-region ssync optimizations, and decides whether to delete the handoff partition. With `handoff_delete` set, a configured number of successful syncs is enough; otherwise all intended syncs must succeed. If using ssync and cross-region syncs reported object sets, it deletes only objects known to be present remotely; otherwise it removes the whole partition. Empty handoff partitions are also removed.

The rsync path builds an rsync command over existing suffix directories, uses xattrs, excludes temporary files, optionally compresses cross-region transfers, then sends a backend `REPLICATE` notification for the synced suffixes unless the job is a failed delete. `_rsync()` bounds subprocess runtime, kills long-running children, hands stubborn child reaping to a background greenlet, limits error log lines if configured, and logs transfer output according to settings.

## State And Persistence
Persistent effects include rsync/ssync writes to remote object servers, local handoff partition deletion via `shutil.rmtree`, per-object handoff cleanup via `delete_handoff_objs()`, stale tmp cleanup through `unlink_older_than()`, and creation of missing object data directories. Replicated object contents, metadata, tombstones, and suffix hash files are owned by the DiskFile layer.

In-memory pass state includes `stats_for_dev`, `partition_times`, `replication_cycle`, `all_devs_info`, `handoffs_remaining`, current ring mtimes, and child rsync processes awaiting reaping. Recon state is persisted in `RECON_OBJECT_FILE`; single-process runs write aggregate `replication_stats`, while multiprocess workers write `object_replication_per_disk` entries and the parent aggregates them only when every current local device has reported.

## Dependencies And Integration Points
The daemon depends on Swift ring placement, `POLICIES` filtered to `REPL_POLICY`, `DiskFileRouter`, backend object-server `REPLICATE`, optional `ssync_sender.Sender`, external `rsync`, `check_drive()`, `is_local_device()`, recon-cache helpers, and eventlet/tpool concurrency. It is launched through `run_daemon(ObjectReplicator, ...)` and accepts CLI overrides for devices, partitions, and policies.

It integrates directly with `obj/server.py` for remote suffix hash retrieval and post-rsync hash invalidation, and with `obj/ssync_sender.py` when configured to use ssync instead of rsync. Handoff cleanup relies on consistent object hashes and storage-directory layout from the DiskFile implementation.

## Risks And Edge Cases
Deletion is the primary operational risk. Handoff partitions or objects are removed only after configured success criteria, but aggressive `handoff_delete` values can trade durability margin for faster rebalance. `delete_handoff_objs()` intentionally removes object hash directories and prunes suffix directories, so object-set calculation from ssync must remain correct.

Other sensitive areas include unmounted drives, rsync subprocess hangs, ring changes mid-pass, `next_part_power` policies, invalid partition files, cross-region deduplication, and multiprocess recon aggregation with stale per-disk entries. The rsync path shells out and depends on remote module interpolation and xattr support; the ssync path depends on protocol compatibility with receivers. Suffix hashes are recalculated before transfer to reduce false positives, but races with live writes are expected and resolved by later passes.

## Test Signals
Focused tests should cover `Stats` aggregation and recon serialization, `_do_listdir()` cycle spreading, rsync argument construction and timeout handling, `update()` suffix-delta/recalc behavior, 507 fallback to handoffs, `revert()` deletion criteria for default and `handoff_delete` modes, `delete_handoff_objs()` suffix pruning, worker device distribution, ring-change aborts, and recon-cache aggregation. Integration tests should exercise both rsync-style REPLICATE notifications and ssync-based handoff cleanup. The local checkout does not include upstream tests, so these signals are inferred from the daemon’s public behavior.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/obj/replicator.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/obj/server.py -->
# sources/object-store/openstack-swift/swift/obj/server.py

## Purpose
Implements the Swift object-server WSGI application. It handles object `PUT`, `GET`, `HEAD`, `POST`, and `DELETE` requests, internal `REPLICATE` hash requests, internal `SSYNC` streaming replication requests, container update fan-out, expiring-object queue updates, metadata validation, DiskFile access, request logging, and optional zero-copy object reads.

## Important APIs, Types, And Functions
Top-level helpers include `iter_mime_headers_and_bodies()` for multipart MIME request bodies, `drain()` for discarding remaining request bytes with timeouts, `get_obj_name_and_placement()` for path/policy validation, and `_make_backend_fragments_header()` for serializing EC fragment metadata.

`EventletPlungerString` is a byte string with inflated length used to force Eventlet WSGI to flush response headers before zero-copy send. `ObjectController` is the main `BaseStorageServer` subclass. Its constructor reads timeouts, chunk sizes, logging flags, upload limits, cache behavior, cooperative iterator period, ETag validation sampling, allowed metadata headers, expirer configuration, and initializes `DiskFileRouter`.

Storage and side-effect helpers include `get_diskfile()`, `async_update()`, `container_update()`, `delete_at_update()`, `_conditional_delete_at_update()`, `_check_container_override()`, and `_post_commit_updates()`. PUT helpers include `_pre_create_checks()`, `_do_multi_stage_mime_continue_headers()`, `_stage_obj_data()`, `_get_request_metadata()`, `_read_mime_footers_metadata()`, `_apply_extra_metadata()`, `_send_multi_stage_continue_headers()`, and `_drain_mime_request()`. Public request handlers are `POST()`, `PUT()`, `GET()`, `HEAD()`, `DELETE()`, `REPLICATE()`, `SSYNC()`, and `__call__()`. `global_conf_callback()` creates a shared replication semaphore, `app_factory()` builds the WSGI app, and `main()` launches `run_wsgi()`.

## Control Flow
All requests enter `__call__()`, which creates a `Request`, records the transaction ID, validates UTF-8/internal path rules, dispatches only public methods, maps DiskFile collisions to 403 and unexpected exceptions to 500, fixes conditional responses, logs normal client traffic at info and replication traffic at debug, optionally delays PUT/DELETE for the `slow` setting, and uses zero-copy send for eligible 200 GET responses.

`PUT()` validates object creation, message length, timestamp freshness, `If-None-Match`, target DiskFile availability, and optional fragment-index/next-part-power headers. It supports proxy multi-stage MIME bodies for metadata footers and multiphase commit: the object body is staged through a DiskFile writer, footer metadata can override allowed sys/user/transient metadata and ETag, the writer is put and optionally committed unless `X-Backend-No-Commit` is set, the remaining MIME stream is drained, expirer/container updates are sent, and 201 is returned.

`POST()` reads existing metadata, enforces newer data or content-type timestamps, writes metafile metadata, conditionally updates expirer tasks, sends a PUT-style container update for object metadata changes, and returns current sysmeta/content-type response headers. It preserves existing data metadata when only content type changes and carries EC override fields into container updates for compatibility.

`GET()` and `HEAD()` open or read the DiskFile with optional fragment preferences and open-expired behavior. They apply conditional ETag support, allowed metadata headers, backend timestamps, durable timestamp, EC fragment listings, content encoding, content length, and cache policy. `GET()` streams a DiskFile reader and may use zero-copy transfer after headers are flushed. Missing, quarantined, expired, state-changed, and xattr unsupported states map to 404, 503, or 507 responses as appropriate.

`DELETE()` validates timestamps, handles existing data, tombstones, expired objects, and `X-If-Delete-At`, updates expirer queues, writes a tombstone when the request is newer, sends a DELETE container update, and returns 204, 404, or 409 with backend timestamp/content-type headers. `REPLICATE()` is an internal replication endpoint that returns pickled suffix hashes for a device/partition/suffix set and skips rehash when suffixes are explicitly supplied. `SSYNC()` instantiates `ssync_receiver.Receiver`, exposes `X-Backend-Accept-No-Commit`, labels metrics with policy, and streams the receiver generator.

## State And Persistence
The object server persists object data files, metadata files, tombstones, non-durable EC fragments, durable commits, async-pending container update pickles, expirer task updates, suffix hashes, quarantine data, and tmp files through DiskFile managers. PUT/POST/DELETE mutate object metadata and container/expirer state; failed container updates are pickled for later async processing. REPLICATE may refresh or return suffix hashes through the DiskFile hash subsystem. SSYNC routes replication subrequests back through the same PUT/POST/DELETE handlers, so replication writes use normal object-server semantics.

Process-level state includes the shared replication semaphore, logger transaction IDs/thread locals, statsd labeled timing labels, tpool sizing, cache/upload configuration, and allowed header sets. The module intentionally changes tpool size for servers-per-port deployments to avoid excessive thread counts.

## Dependencies And Integration Points
The server is the integration point for Swift proxy object requests, object replicator/reconstructor backend traffic, ssync receiver, container servers, object expirer, DiskFile implementations, storage policies, statsd, Eventlet WSGI, and recon/replication daemons. It depends on `DiskFileRouter`, request helper metadata classification, `http_connect` for container updates, expirer task construction, swob response classes, object constraints, and concurrency primitives.

Important protocol contracts include backend storage policy headers, `X-Backend-Replication`, `X-Backend-Replication-Headers`, `X-Backend-Ssync-Frag-Index`, `X-Backend-No-Commit`, `X-Backend-Fragment-Preferences`, container update override prefixes, delete-at headers, and pickled REPLICATE hash responses. `global_conf_callback()` must run before worker fork so the replication semaphore is shared across object-server workers.

## Risks And Edge Cases
This file is concurrency- and persistence-sensitive. Timestamp ordering protects newer data and metadata, but live writes can still race with reads, replication, and deletes; `DiskFileStateChanged` returns 503 to force retries when on-disk files shift mid-operation. Multi-stage MIME PUT must validate footer MD5/JSON, drain request bodies, send correct 100-continue phases, and avoid committing bad data. `X-Backend-No-Commit` support is essential for EC non-durable fragment replication.

Async container and expirer updates are best-effort and can redirect or fall back to local async-pending pickles; bad container path headers, mismatched host/device lists, or inconsistent expirer container names can create delayed or orphaned side effects. REPLICATE uses pickle protocol 2 for compatibility, so callers must treat it as a trusted internal endpoint. Zero-copy send bypasses normal iterator reads after headers are flushed and must correctly handle socket options and exceptions.

## Test Signals
High-value tests should cover PUT timestamp conflicts, `If-None-Match`, multipart footer validation, ETag mismatch, `X-Backend-No-Commit`, metadata header copying, POST content-type timestamp ordering, DELETE tombstone and `X-If-Delete-At` behavior, expirer update creation/removal, async container update fallback and redirect handling, GET/HEAD backend timestamp/fragment headers, REPLICATE hash response and skip-rehash behavior, SSYNC receiver wiring, request logging levels, and zero-copy eligibility. The local source shard lacks upstream tests, so test signals are inferred from the request handlers and internal protocol contracts.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/obj/server.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/obj/ssync_receiver.py -->
# sources/object-store/openstack-swift/swift/obj/ssync_receiver.py

## Purpose
Implements the receiver side of Swift’s SSYNC replication protocol. The receiver runs inside the object server’s `SSYNC` response body, validates the target device/partition/policy, compares the sender’s offered object hashes and timestamps with local DiskFiles, returns wanted data/meta parts, accepts streamed PUT/POST/DELETE subrequests, routes them through `ObjectController`, and reports protocol errors back to the sender.

## Important APIs, Types, And Functions
`SsyncClientDisconnected` marks early client disconnects. `decode_missing(line)` parses sender-advertised object hash, data timestamp, optional metadata/content-type timestamp deltas, and durability into a dict. `encode_wanted(remote, local)` compares remote and local timestamp state and returns a wanted line containing `d` for data and/or `m` for metadata.

`SsyncInputProxy` wraps `wsgi.input` with timeout-aware `read_line()` and `_read_chunk()` methods. It stores the first exception and re-raises it on later reads so the receiver and object subrequests cannot continue reading from an uncertain stream. `make_subreq_input()` exposes a bounded file-like iterator for a PUT subrequest body.

`SsyncAnnotatedLogger` prefixes receiver logs with remote address and target device/partition. `Receiver` owns request initialization, semaphore/replication lock management, missing-check comparison, and update subrequest routing. Its main methods are `initialize_request()`, `_check_local()`, `_check_missing()`, `missing_check()`, `updates()`, and `__call__()`.

## Control Flow
`Receiver.__init__()` immediately calls `initialize_request()`, which sets Eventlet minimum write chunk size to zero, parses device/partition/policy, validates optional `X-Backend-Ssync-Frag-Index`, validates device/partition names, resolves the DiskFile manager, verifies the device is mounted, and wraps the request input.

`__call__()` first yields a blank line to force response headers and start the bidirectional exchange. It then tries to acquire the shared replication semaphore without blocking, takes a DiskFile replication lock for the target partition, runs `missing_check()`, then runs `updates()`. Known timeout/read/HTTP/lock errors are converted into SSYNC `:ERROR:` protocol lines when possible; client disconnects and broken reads cause early socket shutdown so the sender stops writing.

During `missing_check()`, the receiver expects `:MISSING_CHECK: START`, reads offered `hash timestamp [extras]` lines until `:MISSING_CHECK: END`, calls `_check_missing()` for each line, accumulates wanted hashes, and then emits its own `:MISSING_CHECK: START`, wanted lines, and `:MISSING_CHECK: END`. `_check_local()` opens the local DiskFile by object hash and optional fragment index, detects local tombstones, data/meta/content-type timestamps, and non-durable EC fragments. If the sender offers a durable fragment that already exists locally only as non-durable, it attempts a local commit and rechecks once.

During `updates()`, the receiver expects `:UPDATES: START`, then repeatedly parses subrequest lines of the form `METHOD PATH`, reads headers until a blank line, creates an internal `swob.Request` rooted at the target device/partition, attaches a bounded body stream for PUT, injects backend policy/replication/fragment-index headers, records replication headers to force metadata preservation, and calls `subreq.get_response(self.app)`. Successful and 404 responses count as success; other responses increment failures and may abort early if the configured failure threshold and ratio are exceeded. After draining each subrequest body, a no-failure run replies with `:UPDATES: START` and `:UPDATES: END`.

## State And Persistence
The receiver itself does not write object files directly. All persistent changes happen by routing subrequests through the object server, so PUT/POST/DELETE use normal DiskFile, async container update, expirer, timestamp, and commit semantics. `_check_local()` may make an existing EC fragment durable by opening a DiskFile writer and committing the offered data timestamp. The receiver also consumes and controls the SSYNC HTTP stream, holds a process-shared replication semaphore, and takes a per-partition replication lock.

## Dependencies And Integration Points
The receiver integrates with `obj/server.py` through `ObjectController.SSYNC()` and subrequest routing. It shares wire encodings with `ssync_sender.encode_missing()` and `ssync_sender.decode_wanted()`, uses `request_helpers.get_name_and_placement()`, DiskFile manager lookup/open/commit APIs, Swift exceptions, swob responses, Eventlet WSGI chunk errors, and object-server replication failure thresholds. Fragment-index handling is shared with EC reconstructor/reconstructor ssync flows.

## Risks And Edge Cases
Protocol synchronization is critical. Missing newlines, early EOF, bad chunk reads, malformed start/end markers, invalid methods, missing PUT content lengths, or unexpected subrequest bodies all abort the session. Because request and subrequest readers share the same underlying stream, `SsyncInputProxy`’s sticky exception behavior prevents unsafe continued reads after a failure.

Durability handling for EC fragments is subtle: a local non-durable fragment may be committed without receiving bytes if the remote advertises it as durable at the same timestamp. Failure thresholds balance avoiding wasted transfer against tolerating occasional subrequest failures. Treating 404 subrequest responses as success is intentional for idempotent deletes and tombstone races, but should remain tested. Semaphore acquisition is non-blocking, so overload returns 503 instead of queueing.

## Test Signals
Useful tests should cover `decode_missing()` timestamp delta/offset/durable parsing, `encode_wanted()` data/meta decision logic, sticky exceptions and newline enforcement in `SsyncInputProxy`, request initialization validation, non-durable-to-durable local commit behavior, missing-check protocol framing, updates subrequest parsing, metadata replication header filtering, failure threshold aborts, socket shutdown on disconnect, and semaphore/replication-lock error responses. Integration tests should pair this receiver with `ssync_sender.Sender` and object-server DiskFile fixtures for PUT/POST/DELETE replication.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/obj/ssync_receiver.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/obj/ssync_sender.py -->
# sources/object-store/openstack-swift/swift/obj/ssync_sender.py

## Purpose
Implements the sender side of Swift’s SSYNC replication protocol. It connects to a remote object server’s `SSYNC` endpoint, advertises local object hashes and timestamps for selected suffixes, receives the remote wanted set, streams PUT/POST/DELETE subrequests for requested data or metadata, and returns the set of objects that are safe to delete from handoff storage.

## Important APIs, Types, And Functions
`encode_missing(object_hash, ts_data, ts_meta=None, ts_ctype=None, **kwargs)` formats a hash, data timestamp, optional metadata/content-type timestamp deltas, offsets, and optional `durable:False` flag into the receiver’s missing-check line format. `decode_wanted(parts)` parses receiver wanted flags, defaulting legacy empty responses to data-only.

`SsyncBufferedHTTPResponse` extends Swift’s buffered HTTP response with a custom `readline()` that understands chunked transfer encoding and preserves an internal SSYNC response buffer. `SsyncBufferedHTTPConnection` binds that response class.

`Sender` is the main protocol client. Constructor inputs are a daemon with logger/timeouts/DiskFileRouter, a target node, a replication/reconstruction job, suffix list, optional `remote_check_objs`, `include_non_durable`, and `max_objects`. Its key methods are `__call__()`, `connect()`, `missing_check()`, `updates()`, `send_subrequest()`, `send_delete()`, `send_put()`, `send_post()`, and `disconnect()`.

## Control Flow
`Sender.__call__()` exits successfully with an empty deletion map when there are no suffixes. Otherwise it connects, performs missing check, and either sends updates or, when `remote_check_objs` is set, only computes which advertised objects are already in sync remotely. It catches expected timeout/replication errors as logged failures and catches unexpected exceptions so callers originally designed around rsync return codes are insulated from Python exceptions.

`connect()` opens a chunked `SSYNC /device/partition` request to the remote replication address, sends the storage policy index, optional backend fragment index and legacy node-index headers, reads the HTTP response, and rejects non-200 statuses. When sending non-durable fragments was requested, it requires the receiver’s `X-Backend-Accept-No-Commit` capability; otherwise it logs a warning and falls back to durable-only behavior.

`missing_check()` sends `:MISSING_CHECK: START`, iterates `df_mgr.yield_hashes()` for the job’s device/partition/policy/suffixes and optional fragment preferences, filters to `remote_check_objs` when supplied, sends encoded missing lines as HTTP chunks, honors `max_objects` truncation, ends the section, then reads the receiver’s wanted section. It returns `available_map` for all advertised objects and `send_map` for objects/parts the receiver wants.

`updates()` sends `:UPDATES: START`, iterates the wanted map, resolves each object hash to a DiskFile, opens it with optional non-durable fragment preferences, and sends the necessary subrequests. Wanted data becomes a PUT; if the job provides `sync_diskfile_builder` (used by the EC reconstructor), that callback can provide a rebuilt fragment stream instead of the local DiskFile. Wanted metadata newer than the data timestamp becomes a POST. Local tombstones become DELETE subrequests. DiskFile errors before bytes are sent are skipped. After `:UPDATES: END`, the sender reads the receiver’s update acknowledgment and treats any unexpected line as a replication exception.

`send_subrequest()` serializes a method/path/header block, sends it as a chunk, streams DiskFile reader chunks when present, and verifies sent bytes equal the advertised content length. `send_put()` copies datafile metadata except name/content length and adds `X-Backend-No-Commit` for non-durable sends; `send_post()` sends metafile metadata when present; `disconnect()` terminates the chunked request with a zero-length chunk and closes the connection.

## State And Persistence
The sender reads local object state through DiskFile manager `yield_hashes()` and `get_diskfile_from_hash()`. It does not mutate local object storage directly, but its return value drives handoff cleanup in `obj/replicator.py` and `obj/reconstructor.py`. `limited_by_max_objects` records partial revert progress. Remote persistence is caused by the subrequests it streams to `ssync_receiver`, which routes them through the remote object server.

In-memory state includes the available and wanted maps, remote-check filters, include-non-durable capability, max-object truncation state, and the chunked response read buffer. Network state is manually synchronized through chunk framing and SSYNC start/end markers.

## Dependencies And Integration Points
The sender depends on Swift buffered HTTP connections, DiskFile manager hash and open APIs, replication exceptions/timeouts, object-server `SSYNC`, receiver capability headers, `ssync_receiver` wire formats, and daemon fields such as `conn_timeout`, `node_timeout`, `http_timeout`, `network_chunk_size`, `_df_router`, and logger. It is used by the replicated-policy `ObjectReplicator` and the EC `ObjectReconstructor`; the latter supplies fragment-index jobs and a `sync_diskfile_builder` callback for rebuilt fragments.

## Risks And Edge Cases
The sender must keep SSYNC and HTTP chunk framing synchronized. `SsyncBufferedHTTPResponse.readline()` closes the connection on malformed chunk sizes or early disconnects because protocol state is likely lost. If a DiskFile reader yields fewer bytes than its content length, the sender aborts the session to avoid finalizing partial remote state. Legacy receiver behavior defaults wanted parts to data-only, which preserves compatibility but cannot sync standalone metadata.

`max_objects` deliberately truncates a revert pass and must prevent local cleanup from assuming completion. `remote_check_objs` performs a check-only session and should not send updates. Non-durable EC fragment replication depends on receiver capability negotiation; older receivers force durable-only behavior. Reconstructed fragment sends depend on metadata from one local fragment and byte streams rebuilt from other nodes, so content-length and ETag handling must stay aligned with object-server PUT validation.

## Test Signals
Tests should cover `encode_missing()` with meta/content-type deltas, offsets, URL quoting, and durable flags; `decode_wanted()` legacy and explicit data/meta behavior; chunked `readline()` with split lines, chunk extensions, EOF, and malformed chunks; `connect()` capability negotiation; `missing_check()` filtering, truncation, and wanted-map parsing; `updates()` PUT/POST/DELETE decisions; byte-count mismatch aborts in `send_subrequest()`; non-durable PUT headers; and check-only deletion-map behavior. Integration coverage should run sender and receiver together for replicated handoffs and EC fragment reconstruction jobs.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/obj/ssync_sender.py -->
