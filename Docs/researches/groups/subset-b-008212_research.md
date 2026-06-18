# subset-b-008212 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/account/server.py -->
# sources/object-store/openstack-swift/swift/account/server.py

Purpose: implements the Swift account-server WSGI controller. It exposes account database operations over internal storage-node HTTP: account create/delete/update/listing, container update fan-in, and account replication RPC dispatch.

Important APIs: `get_account_name_and_placement()` and `get_container_name_and_placement()` validate storage-node paths and internal account/container names. `AccountController` derives from `BaseStorageServer`; `_get_account_broker()` maps account names to hashed account DB paths under `devices/<drive>/accounts/...`; `_deleted_response()`, `check_free_space()`, `_update_metadata()`, and public `DELETE`, `PUT`, `HEAD`, `GET`, `REPLICATE`, `POST` implement the request surface. `app_factory()` and `main()` wire paste.deploy and `run_wsgi`.

Control flow: `__call__()` builds a `Request`, rejects invalid UTF-8 and non-public methods, dispatches to the method named by `req.method`, translates raised `HTTPException` or unexpected exceptions, and logs a Swift request line. `PUT` has two branches: account creation/metadata update, or container row update from container-server notifications. `GET` and `HEAD` use stale-read brokers with short pending timeouts for fast listing/stat responses. `REPLICATE` parses JSON from `wsgi.input` and delegates to `ReplicatorRpc`.

State and persistence: persistent state lives in account SQLite DBs managed by `AccountBroker`; metadata values are timestamped and validated. Container rows store put/delete timestamps, object counts, bytes used, and storage policy index. Delete is logical database deletion. Free-space and mount checks gate mutating requests and replication.

Dependencies and integration: integrates with Swift constraints, request helpers, listing format negotiation, account backend, DB replicator, storage directory hashing, and swob HTTP responses. It is invoked by storage-node WSGI and by container/account replicators.

Risks: correctness depends on timestamp ordering, internal-name validation, broker pending-file behavior, and consistent policy index propagation. Auto-created internal accounts bypass normal account creation only for the configured prefix. Error paths expose tracebacks in 500 bodies. Missing required container-update headers will surface as server errors rather than friendly validation.

Test signals: exercise every HTTP verb, deleted-account states, mount/free-space failures, metadata validation, container update created-vs-deleted response, JSON replication parse failures, invalid UTF-8, logging behavior, and stale-read fallback paths.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/account/server.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/account/utils.py -->
# sources/object-store/openstack-swift/swift/account/utils.py

Purpose: shared helpers for account responses and account listing serialization. It centralizes account stat headers and the account listing body used by the account server and tests.

Important APIs: `FakeAccountBroker` is a minimal broker-like object for empty account responses. `get_response_headers(broker)` converts broker info, policy stats, and account metadata into HTTP headers. `account_listing_response()` obtains container rows from `broker.list_containers_iter()` and formats XML, JSON, plain-text, or empty `204` responses.

Control flow: `account_listing_response()` defaults to `FakeAccountBroker`, builds headers first, then transforms broker rows into dictionaries. Subdir rows become `{'subdir': name}`; container rows include name, count, bytes, last_modified, and storage policy name when the policy index exists. Content type suffix selects XML, JSON, text, or no-content response.

State and persistence: no direct persistence; all state comes from the broker. Response headers expose account counts, bytes, creation and PUT timestamps, storage-policy stats, and non-empty broker metadata.

Dependencies and integration: uses `Timestamp`, `POLICIES`, account listing limits, listing format utilities, and swob responses. `server.py` uses both exported helpers for `GET` and `HEAD`.

Risks: metadata with empty values is suppressed, unknown policy indexes intentionally omit storage-policy names, and JSON output is ASCII encoded. Tests should cover policy stats, reserved-name allowance forwarding, delimiter/subdir listings, empty account responses, and every response format.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/account/utils.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/__init__.py -->
# sources/object-store/openstack-swift/swift/cli/__init__.py

Purpose: package marker for Swift command-line tools. The file is empty and exports no runtime APIs.

Important APIs/types/functions: none. Its significance is structural: it allows modules under `swift.cli` to be imported by console-script entry points and by other modules, such as `swift.cli.get_nodes` importing helpers from `swift.cli.info`.

Control flow: none.

State and persistence: none.

Dependencies and integration: participates in Python package discovery for operational commands including recon, info, dispersion, account auditing, shard-range management, and process tools.

Risks and test signals: operational risk is limited to packaging. Tests or packaging checks should verify `swift.cli.*` imports and console entry points resolve when installed.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/account_audit.py -->
# sources/object-store/openstack-swift/swift/cli/account_audit.py

Purpose: operational consistency auditor for accounts, containers, and objects. It walks Swift rings, talks directly to storage nodes, compares listings/counts/ETags across replicas, and optionally downloads objects to verify checksums.

Important APIs: `Auditor.__init__()` loads account, container, and object rings and initializes counters, caches, and in-progress events. `audit_account()`, `audit_container()`, and `audit_object()` perform replica-level checks. `audit()` chooses depth from a parsed path; `wait()` joins green threads; `print_stats()` summarizes mismatches. `main()` parses `-c`, `-r`, `-e`, `-d`, arguments, and stdin paths.

Control flow: account audit gets all account replicas, pages JSON listings by marker, compares account container/object counts, caches container names, and optionally recurses into containers. Container audit first verifies account listing membership, then pages every container replica, compares object versions and object counts, caches object listings, and optionally spawns object audits. Object audit verifies container listing membership, HEADs or GETs each object replica, checks ETags and optional MD5, and writes inconsistent paths to the error file.

State and persistence: mostly read-only network probing. Persistent output is optional append-only error-file entries. In-memory `list_cache` and `in_progress` events avoid duplicate concurrent listing fetches.

Dependencies and integration: uses Swift `Ring`, `http_connect`, `split_path`, eventlet `GreenPool`/`Event`, direct storage-node endpoints, and MD5 helpers.

Risks: can generate heavy direct-node load, especially with deep download mode. It assumes JSON listing format and specific replica headers. A small bug prints an account error path with `print(path, error_file)` instead of `file=error_file`. Unicode path encoding differs by account/container/object segment.

Test signals: mock rings and HTTP responses for replica divergence, marker paging, cache synchronization, deep checksum mismatch, error-file writes, stdin path parsing, and counter summaries.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/account_audit.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/config.py -->
# sources/object-store/openstack-swift/swift/cli/config.py

Purpose: prints Swift server configuration in a flattened, operator-readable form. It can inspect normal config files or paste.deploy WSGI pipeline configs.

Important APIs: module-level `parser`, `_context_name()`, `inspect_app_config()`, and `main()`. `inspect_app_config()` extracts a paste context, filters, app context, and reconstructed pipeline string.

Control flow: `main()` parses server or config path arguments. Each argument is either an existing file or a server name resolved through `Server(arg).conf_files()`. For each config, it prints the file path, loads either `appconfig()` or `readconf()`, filters by section when requested, prints dict sections as INI sections, and prints scalar values as commented lines.

State and persistence: read-only; no config mutation.

Dependencies and integration: uses Swift `Server` manager discovery, `readconf`, and `appconfig`. It is a support tool for deployed operators checking effective config.

Risks: values are printed verbatim, so secrets in configs can be exposed to terminal logs. Section filtering is exact. Paste inspection assumes pipeline object context shape. Tests should cover file-vs-server lookup, WSGI pipelines, scalar config values, section filtering, and missing-argument error return.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/config.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/container_deleter.py -->
# sources/object-store/openstack-swift/swift/cli/container_deleter.py

Purpose: enqueues async-delete jobs for a range of objects in one container, letting the object expirer delete them later while listings may still show them until expiration processing catches up.

Important APIs: `OBJECTS_PER_UPDATE`, `make_delete_jobs()`, `mark_for_deletion()`, and `main()`. `make_delete_jobs()` creates expirer queue update rows using `build_task_obj()` and `ASYNC_DELETE_TYPE`. `mark_for_deletion()` is usable as a generator for progress and retry markers.

Control flow: the tool lists objects through `InternalClient.iter_objects()` with marker/end-marker/prefix. It batches up to 10,000 object names, builds async-delete rows at a single timestamp, sends an internal `UPDATE` to `.expiring_objects/<timestamp>`, and yields progress periodically with the last processed object. `main()` constructs an `InternalClient` and prints progress or final count.

State and persistence: writes expirer queue objects via internal Swift requests; it does not delete user objects directly. Timestamp selection controls delete task identity and target expirer container.

Dependencies and integration: depends on `InternalClient`, object-expirer task naming, Swift timestamps, and private backend headers.

Risks: duplicates may be enqueued on retry before the last marker; the code intentionally reports the last object to reduce that. The default `--timestamp` is created when argparse is built, not at loop time, but `main()` constructs the parser per invocation. Large containers can produce sustained internal load.

Test signals: cover job payload shape, batching, generator vs count mode, marker/end-marker/prefix forwarding, backend headers, failed internal requests, and retry progress semantics.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/container_deleter.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/dispersion_populate.py -->
# sources/object-store/openstack-swift/swift/cli/dispersion_populate.py

Purpose: creates sample containers and objects spread across ring partitions so `swift-dispersion-report` can later measure missing replica coverage.

Important APIs: `put_container()`, `put_object()`, `report()`, and `main()`. Global counters track created items, retries, ETA, and current item type.

Control flow: `main()` monkey-patches eventlet, reads `dispersion.conf`, authenticates, chooses a storage policy, builds a `SimpleClient` pool, and separately populates containers and/or objects. For each target partition, it increments suffixes until ring placement hits an uncovered partition. `--no-overlap` first lists existing dispersion resources and removes already-covered partitions. GreenPool tasks create containers or objects and update progress.

State and persistence: writes real Swift containers named `dispersion_<policy>_<suffix>` and a container `dispersion_objects_<policy>` with objects named `dispersion_<suffix>`. Object data is the object name and metadata includes `x-object-meta-dispersion`.

Dependencies and integration: uses `swiftclient` or internal auth fallback, `SimpleClient`, Swift rings, storage policies, config parser, and eventlet pools.

Risks: it creates user-visible account resources and can collide with existing dispersion resources if prefixes are reused. Coverage math is partition-based, not replica-health-based. Authentication config and policy selection errors terminate with `exit()`.

Test signals: mock ring placement and client calls for coverage, no-overlap behavior, suffix-start options, policy lookup, retries accounting, and disabled object/container modes.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/dispersion_populate.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/dispersion_report.py -->
# sources/object-store/openstack-swift/swift/cli/dispersion_report.py

Purpose: checks the dispersion resources created by `dispersion_populate` and reports what percentage of expected container/object replica copies are reachable on their primary nodes.

Important APIs: `get_error_log()`, `container_dispersion_report()`, `object_dispersion_report()`, `missing_string()`, `generate_report()`, and `main()`.

Control flow: `main()` reads config and option overrides, then `generate_report()` authenticates, builds a client pool, loads container and policy object rings, and calls selected report functions. Container report lists dispersion containers from the account, deduplicates by partition, and HEADs each primary container replica with `direct_client.retry()`. Object report lists objects in the policy-specific dispersion object container, deduplicates by object partition, and HEADs object replicas with optional backend policy headers. Both functions aggregate found/expected copies, missing-copy distribution, overlap count, retries, and optional JSON output.

State and persistence: read-only cluster probing. Module-level globals hold output/debug flags and de-duplicate unmounted/notfound error messages.

Dependencies and integration: uses direct client calls, storage policies, rings, SimpleClient auth, eventlet, and recon-style operator output. It consumes resources created by `dispersion_populate`.

Risks: reports only sampled partitions and primary nodes, so it is a health signal rather than a full audit. Missing 404 and 507 handling is intentionally special-cased. A policy object header is only used in object checks. Large samples can create many direct requests.

Test signals: cover empty-population warnings, JSON vs text outputs, missing partition printing, retry accounting, 404/507 suppression, overlapping partition math, policy selection, and config option overrides.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/dispersion_report.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/drive_audit.py -->
# sources/object-store/openstack-swift/swift/cli/drive_audit.py

Purpose: scans kernel logs for device errors, maps kernel devices to mounted Swift device paths, optionally unmounts failed devices and comments `/etc/fstab`, then writes recon cache error counters.

Important APIs: `get_devices()`, `get_errors()`, `comment_fstab()`, and `main()`.

Control flow: `main()` reads `[drive-audit]` config, builds regexes from config or defaults, initializes logging, discovers mounted devices below `device_dir`, scans recent matching log files backwards until the time window or boot boundary, and counts matching kernel device errors. Devices exceeding `error_limit` are either logged or unmounted with `umount -fl` and removed from fstab. Recon cache is updated with per-mount errors and total `drive_audit_errors`; systemd daemon reload runs after fstab edits.

State and persistence: reads `/dev/block`, `/proc/mounts`, `/proc/partitions`, and log files. It may mutate mount state and `/etc/fstab`; it writes recon cache files under `recon_cache_path`.

Dependencies and integration: uses Swift `backward`, logging, `dump_recon_cache`, recon middleware consumption, and OS commands/files.

Risks: high operational blast radius if regexes match incorrectly or device mapping is wrong. `comment_fstab()` rewrites `/etc/fstab` via `/etc/fstab.new`. Time parsing depends on locale and log format, with special handling for year rollover and ISO timestamps.

Test signals: mock proc/dev/log inputs, year rollover, ISO timestamps, regex config, unmount disabled/enabled paths, fstab rewrite, recon cache writes, and no-device behavior.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/drive_audit.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/form_signature.py -->
# sources/object-store/openstack-swift/swift/cli/form_signature.py

Purpose: generates a FormPost middleware HMAC signature and sample HTML form for browser uploads.

Important APIs: `main(argv)` validates positional arguments, computes expiry, signs the five-line FormPost payload using HMAC-SHA1, prints the signature, and emits a sample multipart form.

Control flow: with incorrect argument count it prints syntax and sample usage. Otherwise it validates non-negative max file size, positive max file count, positive seconds, and a `/v1/account/container[/prefix]` path. It signs `path`, `redirect`, `max_file_size`, `max_file_count`, and `expires` joined by newlines using the supplied key encoded as UTF-8.

State and persistence: no persistence; output goes to stdout. The only time-dependent state is `expires = now + seconds`.

Dependencies and integration: matches Swift FormPost middleware signature semantics and account temp URL key usage.

Risks: prints sample HTML containing raw path and redirect values without escaping, so output should be treated as operator guidance rather than sanitized templating. SHA1 is protocol-defined here. Tests should cover argument validation, exact signing payload, byte/unicode key behavior, and generated form fields.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/form_signature.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/get_nodes.py -->
# sources/object-store/openstack-swift/swift/cli/get_nodes.py

Purpose: command-line wrapper that shows which storage nodes own a Swift account, container, object, or raw partition.

Important APIs: `main()` only; core parsing and printing are delegated to `swift.cli.info.parse_get_node_args()` and `print_item_locations()`.

Control flow: parses `--all`, `--partition`, `--policy-name`, `--swift-dir`, and `--quoted`. It sets the Swift directory and reloads storage policies when needed, validates ring/path arguments, optionally loads a ring from a `.ring.gz` file, derives ring name from the filename, and prints locations. `InfoSystemExit` is converted into help text plus an error or exit code.

State and persistence: read-only; it loads local ring files and storage-policy config.

Dependencies and integration: depends on `Ring`, storage-policy reload, and `info.py` helper functions. It is a thin console entry point for ring placement inspection.

Risks: output is only as current as local ring files. Passing the wrong ring with a path type can produce warnings or misleading operator commands. Tests should cover quoted path parsing, policy-name object lookup, partition lookup, invalid ring paths, handoff inclusion, and error exits.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/get_nodes.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/info.py -->
# sources/object-store/openstack-swift/swift/cli/info.py

Purpose: shared implementation for `swift-account-info`, `swift-container-info`, `swift-object-info`, and `swift-get-nodes` style introspection. It reads DBs/datafiles, prints metadata and sync/sharding state, and computes ring placement plus direct curl/ssh hints.

Important APIs: `InfoSystemExit`, `parse_get_node_args()`, `curl_head_command()`, `print_ring_locations()`, `print_db_info_metadata()`, `print_obj_metadata()`, `print_info()`, `print_obj()`, `print_item_locations()`, and entry points `obj_main()`, `container_main()`, `account_main()`.

Control flow: DB info opens an `AccountBroker` or `ContainerBroker`, reads broker info and metadata, adds deletion and shard-range details, prints metadata grouped by user/system prefixes, optionally prints sync tables, then attempts ring placement. Object info reads diskfile metadata, prints object metadata including crypto details, optionally streams the file to verify ETag/content length, extracts policy from path, and prints ring locations. `print_item_locations()` selects account/container/object ring behavior from supplied path, ring, policy, or partition.

State and persistence: read-only, except it may trigger broker pending commit behavior indirectly through broker reads depending on backend behavior. It reads SQLite DBs, object datafiles, rings, and swift config.

Dependencies and integration: uses account/container brokers, diskfile metadata, storage policies, ring hashing, metadata prefix helpers, crypto metadata decoding, SQLite, and lock-timeout fallback.

Risks: object ETag checking reads whole datafiles and can be expensive. `print_obj_metadata()` mutates its metadata dict with `pop()`. Stale DB reads are retried after `OperationalError` or `LockTimeout`, exiting with code 2. Incorrect policy/ring combinations print warnings but still produce output.

Test signals: cover DB type validation, stale-read fallback, shard-range summary/verbose output, sync-table output, object crypto metadata, ETag mismatch, IPv6 curl formatting, policy extraction, quoted get-node args, and all entry-point exit paths.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/info.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/manage_shard_ranges.py -->
# sources/object-store/openstack-swift/swift/cli/manage_shard_ranges.py

Purpose: operator tool for finding, installing, enabling, compacting, repairing, and analyzing container shard ranges by directly modifying one container database replica.

Important APIs: command functions `find_ranges()`, `show_shard_ranges()`, `db_info()`, `delete_shard_ranges()`, `merge_shard_ranges()`, `replace_shard_ranges()`, `find_replace_shard_ranges()`, `enable_sharding()`, `compact_shard_ranges()`, `repair_shard_ranges()`, `analyze_shard_ranges()`, parser builder `_make_parser()`, and `main()`. Exceptions distinguish gaps, invalid state, and invalid repair solutions.

Control flow: `main()` parses a subcommand, loads optional container-sharder config for default values, validates config, and either analyzes JSON input or opens a `ContainerBroker`. Find scans broker rows into shard data. Replace validates contiguous ranges against the broker own shard range, deletes existing ranges, merges new ranges, and optionally enables sharding. Enable updates the own shard range to SHARDING, stamps epoch, updates stats, and writes `X-Container-Sysmeta-Sharding`. Compact finds small shard sequences and marks donors/acceptors for sharder processing. Repair either expands active neighbors into gaps or chooses a complete acceptor path and finalizes overlapping donors as shrinking.

State and persistence: directly mutates container DB shard-range rows, own shard range, metadata, deleted flags, timestamps, and compaction/repair states. It may commit pending updates unless `--skip-commits` is used.

Dependencies and integration: deeply integrated with `ContainerBroker`, `ShardRange`, `ShardRangeList`, `CleavingContext`, and container sharder algorithms/config. Replicator and sharder daemons consume the DB changes later.

Risks: high blast radius; docs warn to run on one replica. Deleting or replacing ranges after enabling sharding can make replicas inconsistent. Repair intentionally rejects sharding/shrinking states and young overlaps to avoid transient false positives. Operator prompts are bypassed by `--yes` and dry-run prevents writes.

Test signals: parser/default config coverage, JSON validation, contiguous range checks, timeout contexts, enable idempotence, compaction selection, gap repair, overlap repair rejection paths, dry-run/yes prompts, invalid DB handling, and analyze-only behavior.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/manage_shard_ranges.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/oldies.py -->
# sources/object-store/openstack-swift/swift/cli/oldies.py

Purpose: lists old Swift daemon processes, optionally as PIDs only for piping to tools like `xargs kill`.

Important APIs: `main()` parses `--age` and `--pids`, runs `ps -eo etime,pid,args --no-headers`, filters known Python Swift executable prefixes, parses elapsed time into hours, and formats output.

Control flow: each process line is ASCII-decoded and split into elapsed time, pid, and args. Non-Swift command prefixes are skipped. Elapsed times with days add `days * 24`; `HH:MM:SS` adds hours; `MM:SS` adds no hours. Processes at or above the threshold are collected and printed as either PIDs or aligned table rows.

State and persistence: read-only process inspection; no signals are sent.

Dependencies and integration: depends on Linux `ps` output format and installed Swift command paths.

Risks: prefix matching is narrow and may miss venv, alternate install paths, or non-CPython launchers. It exits on unexpected parse formats. Tests should mock `subprocess.Popen` output for day/hour formats, prefix filtering, PIDs-only output, no matches, and malformed lines.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/oldies.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/orphans.py -->
# sources/object-store/openstack-swift/swift/cli/orphans.py

Purpose: lists and optionally signals Swift processes that are not represented by pid files under the Swift run directory.

Important APIs: `main()` parses age, kill signal, wide output, and alternate run directory. It reads `.pid` and `.pid.d` files, includes child processes of those PIDs, scans `ps`, filters Swift commands, excludes known live PIDs and commands containing `once`, then prints or signals the remaining old processes.

Control flow: run-dir walk builds the protected PID set. Process scanning parses elapsed time like `oldies.py`, applies regex matching for `/usr/bin/python[23]? /usr(/local)?/bin/swift-`, skips protected/once processes, and collects old orphan rows. Optional signal names or numbers are resolved and sent via `os.kill()`.

State and persistence: reads pid files and process table; optional side effect is sending signals to matched processes.

Dependencies and integration: uses `swift.common.manager.RUN_DIR`, Linux `ps`, signal constants, and Swift daemon pid-file conventions.

Risks: stale/missing pid files can cause legitimate daemons to be reported as orphaned. Signal mode is destructive. Regex does not cover all possible install paths. Tests should mock run-dir files, child PID discovery, elapsed parsing, `once` exclusion, output clipping, signal translation, and kill calls.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/orphans.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/recon.py -->
# sources/object-store/openstack-swift/swift/cli/recon.py

Purpose: cluster reconnaissance CLI that queries recon middleware endpoints on storage nodes discovered from rings and summarizes health, consistency, and operational metrics.

Important APIs: helpers `seconds2timeunit()` and `size_suffix()`, `Scout` for one-host HTTP requests, and `SwiftRecon` with checks for ring md5, swift.conf md5, async pendings, drive audit, unmounted devices, server type, expirer, reconstruction, replication, updater, auditor, object auditor, sharding, load, quarantine, socket usage, disk usage, time sync, and Swift versions. `main()` instantiates and runs `SwiftRecon`.

Control flow: CLI parses server types and check flags. For each server type, `_get_ring_names()` chooses relevant rings, `get_hosts()` extracts unique `(ip, port)` pairs with optional region/zone filters, and selected checks run through a `GreenPool`. `Scout.scout()` performs `GET /recon/<type>` and parses JSON; `scout_server_type()` sends `OPTIONS /`. Check methods aggregate returned values with `_gen_stats()`, print distributions, compare local file hashes, or identify mismatches.

State and persistence: read-only network probing plus local reads of ring files and `swift.conf`. It maintains only in-memory output and stats.

Dependencies and integration: recon middleware endpoints, Swift rings and storage policies, eventlet/urllib, local config hashes, and operator terminal output.

Risks: many assumptions about recon JSON keys can raise KeyError with older/newer middleware. `--all` can create broad concurrent polling across all storage nodes. Disk usage deduplicates by host and arbitrary port. Time checks depend on request latency bounds and configured jitter.

Test signals: mock `Scout` responses for each endpoint, no-host and partial-error cases, policy selection, region/zone filtering, hash mismatch, disk top/lowest output, auditor nested stats, and CLI flag gating per server type.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/recon.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/recon_cron.py -->
# sources/object-store/openstack-swift/swift/cli/recon_cron.py

Purpose: periodic object-server cron helper that counts async pending update files and writes recon cache values consumed by recon middleware and `swift-recon`.

Important APIs: `get_async_count(device_dir)` and `main()`.

Control flow: `main()` requires an object-server config path, reads the `filter:recon` section, derives device directory, recon cache path, and lock path, then takes a lock named `swift-recon-object-cron`. Under the lock it calls `get_async_count()`, which walks devices and counts entries in `async_pending` or policy-specific `async_pending-*` hash directories. It dumps `async_pending` and `async_pending_last` to the object recon cache file.

State and persistence: reads device directories and writes a recon cache JSON file. Locking prevents overlapping cron instances.

Dependencies and integration: uses `readconf`, `lock_path`, `listdir`, `dump_recon_cache`, `RECON_OBJECT_FILE`, and `ASYNCDIR_BASE`. Its output feeds recon middleware `/recon/async`.

Risks: directory walk cost scales with devices and pending hashes. Exceptions while accessing devices are logged and return error code 1. Tests should cover policy-specific async dirs, non-directory entries, locking, config defaults, recon cache payload, and exception handling.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/recon_cron.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/reconciler_enqueue.py -->
# sources/object-store/openstack-swift/swift/cli/reconciler_enqueue.py

Purpose: debugging/development CLI to manually enqueue a misplaced object operation for the container reconciler.

Important APIs: module-level `parser` and `main()`. `main()` parses policy index, full `/a/c/o` path, timestamp, operation `PUT`/`DELETE`, and `--force`.

Control flow: enables eventlet hub exception debugging, parses args, loads the container ring from `/etc/swift/container.ring.gz`, resolves the policy by index, validates and splits the object path, then calls `add_to_reconciler_queue()`. It prints the reconciler container name on success and returns error strings for invalid policy, invalid path, or failed enqueue.

State and persistence: writes to the reconciler queue through container-ring placement via `add_to_reconciler_queue()`. It does not touch object data directly.

Dependencies and integration: depends on `Ring`, `POLICIES`, `split_path`, eventlet, and `swift.container.reconciler`.

Risks: hard-coded `/etc/swift/container.ring.gz` limits testability and alternate deployments. Manual enqueue with wrong policy/timestamp/op can cause reconciler churn or incorrect repair attempts. Tests should mock policy lookup, path parsing, queue insertion, force behavior, invalid args, and error return strings.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/reconciler_enqueue.py -->
