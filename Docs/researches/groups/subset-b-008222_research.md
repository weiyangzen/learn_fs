# Research: subset-b-008222

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/utils/logs.py -->
# sources/object-store/openstack-swift/swift/common/utils/logs.py

## Purpose
This module centralizes Swift logging behavior for daemons, WSGI servers, request access logs, and stdio capture. It adapts Python logging for eventlet, syslog, Swift transaction context, backend access-log formatting, optional anonymization, and custom operator handlers. It is a shared utility, so changes here affect most Swift services.

## Important APIs, Types, and Functions
- `logging_monkey_patch()` replaces `logging._lock`, registers Swift's `NOTICE` level, maps syslog notice priority, and disables thread logging to avoid deadlocks under monkey patching.
- `PipeMutex` implements a recursive green-thread-aware mutex using an OS pipe so real threads and eventlet greenthreads can coordinate on logging handlers. It disables eventlet's multiple-reader guard.
- `NoopMutex` is the default syslog handler lock for UDP/UDS logging and deliberately avoids serialization while still disabling eventlet multiple-reader detection.
- `ThreadSafeSysLogHandler.createLock()` selects `NoopMutex` unless `SWIFT_NOOP_LOGGING_MUTEX` is false-like, otherwise uses `PipeMutex`.
- `SwiftLogAdapter` wraps loggers with server name, prefix, thread-local `txn_id` and `client_ip`, a `notice()` method, and exception normalization for common socket, HTTP, disk, and timeout failures.
- `SwiftLogFormatter` injects server identity, appends transaction and client IP context when absent from messages, flattens newlines as `#012`, and truncates long lines using middle elision.
- `LoggerFileObject` redirects stdout/stderr into logging while guarding against recursive logging-handler failures.
- `get_swift_logger()` constructs/replaces syslog and optional console handlers from config keys such as `log_facility`, `log_level`, `log_address`, `log_udp_host`, `log_max_line_length`, and `log_custom_handlers`.
- `capture_stdio()` replaces uncaught exception handling and redirects stdio to `LoggerFileObject`, except fds already used by configured console logging.
- `StrAnonymizer`, `StrFormatTime`, `LogStringFormatter`, `get_log_line()`, and `get_policy_index()` build backend access log lines with formatted time, request path parts, anonymization, policy index extraction, and safe default fields.

## Control Flow and Behavior
Logger creation removes any previous handler stored in `get_swift_logger.handler4logger` before adding the new configured syslog handler, so the last call controls handler configuration for a logger route. Console logging is similarly tracked in `console_handler4logger`; once a console handler map exists, later calls refresh console handlers even if `log_to_console` is false. `SwiftLogAdapter.process()` injects extra logging fields on every log call, while `exception()` decides whether to log a compact operational message or a full traceback depending on exception type and errno.

Access log construction in `get_log_line()` derives path components via `split_path`, wraps sensitive fields in `StrAnonymizer`, and formats through `LogStringFormatter(default='-')`. The anonymizer hashes only when a non-empty value exists and uses Swift's md5 helper with `usedforsecurity=False` for md5.

## State and Persistence
Persistent external state is limited to process logging configuration, class-level thread/greenthread local fields, handler maps attached to `get_swift_logger`, environment-variable configuration for logging mutex behavior, and stdio replacement in `capture_stdio()`. `PipeMutex` owns OS pipe fds and closes them in `close()` and `__del__()` to avoid test-suite fd leaks.

## Dependencies and Integration Points
The module depends on eventlet primitives from `swift.common.concurrency`, Swift config parsing helpers, Swift exception types, Python `logging`/`SysLogHandler`, and request objects with WebOb-like attributes. It is integrated by `swift.common.wsgi`, daemon startup, backend servers, proxy logging middleware, and custom handler hooks named by `log_custom_handlers`.

## Risks and Edge Cases
- Logging configuration is global by route; repeated `get_swift_logger()` calls replace handlers and can surprise tests or embedded apps.
- `capture_stdio()` mutates `sys.stdout`, `sys.stderr`, and `sys.excepthook`, which is process-wide.
- `NoopMutex` is safe only under Swift's assumptions about UDP/UDS syslog message boundaries; switching transports or handlers can alter concurrency safety.
- `StrAnonymizer` encodes data and salt as latin-1, so unexpected non-latin-1 values can fail.
- Access-log format strings are operator-controlled and may raise if they reference invalid `StrFormatTime` directives.
- Recursive logging from syslog failures is explicitly mitigated, but handler errors still risk log loss.

## Test Signals
Useful tests should cover logger reconfiguration idempotency, NOTICE level mapping, eventlet/thread mutex recursion and close behavior, exception message normalization by errno and timeout class, stdio recursion guards, anonymized and quoted access-log formatting, policy-index byte/string handling, custom handler import failures, and max-line truncation.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/utils/logs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/utils/pickle.py -->
# sources/object-store/openstack-swift/swift/common/utils/pickle.py

## Purpose
This small module provides durable pickle writes and restricted pickle reads for the limited Swift data structures that still use pickle serialization. It narrows the default Python pickle attack surface by whitelisting the globals required by Swift's legacy serialized data.

## Important APIs, Types, and Functions
- `write_pickle(obj, dest, tmp=None, pickle_protocol=0)` serializes an object to a temporary file, flushes and `fsync()`s it, then atomically renames it into place with Swift's `renamer()`.
- `_ALLOWED_GLOBALS` is the whitelist for unpickling globals: `_codecs.encode`, `copyreg._reconstructor`, `HeaderKeyDict`, `dict`, and `bytes`, with Python 2 compatibility aliases.
- `RestrictedUnpickler.find_class()` permits only whitelisted `(module, name)` pairs and raises `pickle.UnpicklingError` for everything else.
- `unpickle(source, encoding='ASCII')` mirrors `pickle.loads()` for bytes or file-like input while using `RestrictedUnpickler`.

## Control Flow and Behavior
`write_pickle()` ensures the temporary directory exists, creates an exclusive temp file with suffix `.tmp`, writes pickle bytes, flushes Python buffers, fsyncs the fd, and performs an atomic rename. `unpickle()` wraps raw bytes in `io.BytesIO`; other sources are passed directly to `pickle.Unpickler`.

## State and Persistence
The module persists serialized state on disk via pickle files. Durability is handled for the file content itself before rename; parent-directory fsync is not done here. The allowed globals table is static module state.

## Dependencies and Integration Points
It depends on `swift.common.header_key_dict.HeaderKeyDict`, `mkdirs()`, and `renamer()`. It integrates with Swift code that needs old pickle formats while enforcing a known-safe set of classes.

## Risks and Edge Cases
- Pickle remains a sensitive format; the whitelist must be kept tight and expanded only after compatibility and security review.
- `pickle_protocol=0` defaults to ASCII protocol for legacy compatibility, which may be slower/larger than modern protocols.
- Atomic rename does not by itself guarantee parent-directory durability after a crash on all filesystems.
- File-like sources passed to `unpickle()` must be positioned correctly by the caller.

## Test Signals
Tests should assert atomic temp cleanup behavior on success/failure, fsync invocation, round-trips for allowed `HeaderKeyDict`, rejection of arbitrary globals, bytes and file-like unpickle inputs, and compatibility with Python 2 module-name aliases embedded in older pickles.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/utils/pickle.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/utils/timestamp.py -->
# sources/object-store/openstack-swift/swift/common/utils/timestamp.py

## Purpose
This module implements Swift's canonical timestamp model. It provides fixed-width, lexicographically sortable normal timestamps and extended internal timestamps with a hex offset used to order otherwise identical object events. It also encodes multiple logical object timestamps into compact database/file-name strings.

## Important APIs, Types, and Functions
- `BaseTimestamp` supplies parsing/creation plumbing, deca-microsecond rounding (`PRECISION = 1e-5`), bounds checks, normal/internal string properties, ordering, hashing, `isoformat`, `from_isoformat`, `ceil`, and inversion.
- `NormalTimestamp` rejects underscores and represents only the normalized float component.
- `Timestamp` adds a non-negative 16-hex-digit offset, `internal`, `short`, `increment_offset()`, `normalized()`, offset-aware truthiness, and offset-aware inversion.
- `encode_timestamps(t1, t2=None, t3=None, explicit=False)` serializes up to three timestamps as a base timestamp plus signed hex deltas.
- `decode_timestamps(encoded, explicit=False)` reverses that encoding and returns `(t1, t2, t3)`, defaulting missing values to previous values unless `explicit=True`.
- `normalize_timestamp()`, `last_modified_date_to_timestamp()`, and `normalize_delete_at_timestamp()` convert external formats into Swift's sortable string conventions.

## Control Flow and Behavior
Construction coerces numeric inputs through `_create()` and non-numeric inputs through `_parse()`, then rounds to a raw deca-microsecond integer and optionally applies `delta`. Comparison uses the `internal` string after coercion, preserving stable sort semantics across normal and extended forms. `Timestamp._parse()` splits at one underscore and validates both count and hex width; `offset` assignment ignores falsy zero, preserving the initialized zero offset.

`encode_timestamps()` stores `t1.short` and appends `+/-` hex deltas for `t2 - t1` and `t3 - t2` only when needed or explicit. This is used by object metadata rows where data, content-type, and metadata timestamps may differ. `decode_timestamps()` reconstructs distinct `Timestamp` objects only for non-zero deltas, preserving any offset in `t1` for equal components.

## State and Persistence
There is no external persistence here, but timestamp strings produced by this module are persisted throughout Swift object, container, and reconciler state. Constants define the on-disk/on-wire contract: `NORMAL_FORMAT`, `INTERNAL_FORMAT`, `SHORT_FORMAT`, `HEX_PART_DIGITS`, `MAX_OFFSET`, and `MAX_RAW_TIME`. `FORCE_INTERNAL` is module-level state used mainly by tests or upgrade scenarios to force extended formatting.

## Dependencies and Integration Points
This module is imported by container backend, reconciler, object metadata handling, database naming, expirer logic, HTTP Last-Modified conversion, and most consistency code. It relies only on Python `datetime`, `functools`, `math`, and `time`, making it a foundational low-level utility.

## Risks and Edge Cases
- Ordering correctness depends on fixed-width normal/internal string formats; changing width or precision would corrupt persisted sort semantics.
- `normalize_delete_at_timestamp()` caps values at `9999999999.99999` to preserve expirer container-name sorting; this is a deliberate long-term limitation.
- `BaseTimestamp.__lt__()` treats out-of-range coerced values specially when bounds checks were bypassed, so tests should cover invalid comparisons.
- Offsets cannot exceed `MAX_OFFSET`, and `delta` cannot move raw time below zero.
- `EPOCH` is timezone-naive while `isoformat` uses UTC-aware conversion then strips the timezone suffix; this is intentional but easy to misuse.

## Test Signals
High-value tests include lexicographic ordering across normal and internal forms, offset increment and max validation, inversion ordering, explicit and implicit multi-timestamp encoding, negative delta rejection, bytes parsing, isoformat round-trips, delete-at clamping, and compatibility with strings lacking extended offsets.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/utils/timestamp.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/wsgi.py -->
# sources/object-store/openstack-swift/swift/common/wsgi.py

## Purpose
This module provides Swift's WSGI configuration loading, pipeline construction, socket binding, eventlet server execution, process-management strategies, request-processor initialization, and helper functions for creating internal subrequests. It is the common startup and in-process WSGI toolkit for Swift proxy and storage services.

## Important APIs, Types, and Functions
- `NamedConfigLoader`, `ConfigDirLoader`, `_loadconfigdir()`, and `ConfigString` extend PasteDeploy to preserve section names, load config directories, and support raw config strings.
- `wrap_conf_type()`, `appconfig`, `loadcontext()`, `loadapp()`, and `load_app_config()` normalize config paths and build PasteDeploy apps/pipelines, allowing the final app to modify the pipeline.
- `get_socket(conf)` validates `bind_port`/`keep_idle`, binds TCP sockets with backlog and retry timeout, optionally wraps testing SSL, and configures keepalive and TCP_NODELAY.
- `RestrictedGreenPool` blocks accept-loop progress when `max_clients == 1`, making single-client mode truly serial.
- `PipelineWrapper` inspects and edits PasteDeploy pipeline contexts before instantiation.
- `run_server()` loads the app, selects Swift HTTP protocol or PROXY protocol, creates the eventlet WSGI server, calls readiness callbacks, and cleans up pools/watchdogs.
- `StrategyBase`, `WorkersStrategy`, and `ServersPerPortStrategy` implement prefork worker lifecycle, seamless reload state transfer, per-port object-server binding, child tracking, stale reload worker cleanup, and listen-socket management.
- `check_config()` and `run_wsgi()` validate config, configure logging, monkey patch, choose a strategy, daemon hygiene, fork workers, handle signals, and perform reload/stop choreography.
- `_initrp()` and `init_request_processor()` load an app plus config/logger for command-line tools or embedded use.
- `WSGIContext`, `make_env()`, `make_subrequest()`, `make_pre_authed_env()`, and `make_pre_authed_request()` support middleware-internal calls and response inspection.

## Control Flow and Behavior
Startup flows through `run_wsgi()`: `check_config()` loads app config via PasteDeploy, sets `swift_dir`, validates configuration, builds a logger, optionally disables fallocate, monkey patches eventlet, loads the app once for validation, and creates either `WorkersStrategy` or `ServersPerPortStrategy`. `run_wsgi()` then cleans daemon hygiene, either runs a no-fork server or enters a parent loop that forks child workers, waits for each child to write `ready`, signals readiness, waits for exits, and responds to SIGTERM/SIGHUP/SIGUSR1.

`WorkersStrategy` owns one listen socket and maintains a fixed worker count. `ServersPerPortStrategy` uses `BindPortsCache` to discover local ring ports and starts a configured number of workers per port, rebinding as ports appear. `StrategyBase.signal_ready()` captures stdio, informs old managers via inherited fd, reads stale worker state, and notifies systemd. SIGUSR1 reload marks sockets close-on-exec, forks a temporary child that closes old sockets after the new process signals readiness, serializes old worker PIDs through `CHILD_STATE_FD_ENV_KEY`, then `execv()`s the current script.

Pipeline loading builds the ultimate app first, allows `modify_wsgi_pipeline()`, then instantiates filters in reverse. It tracks a separate `ProxyLoggingMiddleware` around the final app so backend internal requests can log correctly.

## State and Persistence
The module mutates process state extensively: signal handlers, environment variables for reload fds, timezone `TZ=UTC+0`, eventlet hub/debug settings, systemd notifications, forked child processes, listen sockets, stdio capture, and global PasteDeploy loader registration. Persistent disk state is not created directly, but config files/directories and ring port caches drive runtime behavior.

## Dependencies and Integration Points
It depends on eventlet and Swift's concurrency facade, PasteDeploy, Swift HTTP protocol classes, constraints, swob `Request`, logging utilities, `BindPortsCache`, daemon hygiene helpers, systemd notification helpers, and storage-policy/ring configuration. It is called by Swift service entrypoints and used by middleware to synthesize subrequests.

## Risks and Edge Cases
- Process management is signal- and fork-heavy; reload fd handling and close-on-exec flags are critical to avoid duplicate listeners or stalled old workers.
- `get_socket()` only warns for inline SSL and assumes external TLS in production.
- Config compatibility depends on PasteDeploy internals that are monkey patched at import time.
- `ServersPerPortStrategy` must handle dynamic ring port changes without leaking sockets or workers.
- `make_env()` copies a curated set of WSGI keys; missing future environment keys can affect middleware subrequests.
- Child readiness depends on exact `b'ready'` pipe writes; worker startup failures raise in the manager.

## Test Signals
Tests should exercise config file, config dir, and config string loading; pipeline modification and request-logging split pipeline attributes; socket bind validation and retries; no-fork versus prefork paths; SIGTERM/SIGHUP/SIGUSR1 behavior; per-port worker registration and stale worker cleanup; systemd notification hooks; generated pre-authorized requests; and `WSGIContext` response capture when apps delay `start_response`.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/wsgi.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/container/__init__.py -->
# sources/object-store/openstack-swift/swift/container/__init__.py

## Purpose
This file is empty. Its purpose is to mark `swift.container` as an importable Python package for container-server components such as backend, auditor, reconciler, updater, replicator, sharder, and server modules.

## Important APIs, Types, and Functions
There are no functions, classes, constants, imports, or exports defined in this file.

## Control Flow and Behavior
There is no runtime control flow. Importing `swift.container` executes no code from this file.

## State and Persistence
There is no in-memory state and no persistence behavior.

## Dependencies and Integration Points
Its integration point is Python package discovery. Sibling modules rely on the package path, but this file does not import or configure them.

## Risks and Edge Cases
Risk is minimal. Adding side effects here would be high blast-radius because any import of `swift.container` would trigger them.

## Test Signals
Package import tests are sufficient. No behavioral unit tests are required while the file remains empty.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/container/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/container/auditor.py -->
# sources/object-store/openstack-swift/swift/container/auditor.py

## Purpose
This module defines the container auditor daemon entrypoint. It specializes Swift's generic `DatabaseAuditor` for container databases by selecting `ContainerBroker` and the `container` server type.

## Important APIs, Types, and Functions
- `ContainerAuditor(DatabaseAuditor)` sets `server_type = "container"` and `broker_class = ContainerBroker`.
- `ContainerAuditor._audit(job, broker)` currently returns `None`, meaning container-specific extra audit checks are not implemented here beyond the generic database auditor behavior.
- `main()` parses daemon options with `parse_options(once=True)` and runs the daemon through `run_daemon(ContainerAuditor, conf_file, **options)`.

## Control Flow and Behavior
CLI execution calls `main()`, which delegates option parsing and daemon lifecycle to shared Swift helpers. During audit runs, the inherited `DatabaseAuditor` opens container DBs through `ContainerBroker`; this subclass does not add per-container validation in `_audit()`.

## State and Persistence
State and persistence are inherited from `DatabaseAuditor` and `ContainerBroker`; this file itself stores no state. The audited persistence target is the SQLite-backed container database tree.

## Dependencies and Integration Points
It depends on `swift.container.backend.ContainerBroker`, `swift.common.daemon.run_daemon`, `swift.common.db_auditor.DatabaseAuditor`, and `swift.common.utils.parse_options`. It integrates with Swift daemon management and config files for container auditor processes.

## Risks and Edge Cases
- The no-op `_audit()` means corruption or invariant checks must come from the generic database auditor; container-specific shard and policy invariants are not checked here.
- Any change to `broker_class` affects which database layout the auditor can inspect.

## Test Signals
Tests should verify daemon option parsing, subclass attributes, that `run_daemon()` is called with `ContainerAuditor`, and that inherited auditor flows instantiate `ContainerBroker` for container database paths.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/container/auditor.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/container/backend.py -->
# sources/object-store/openstack-swift/swift/container/backend.py

## Purpose
This module implements Swift's SQLite-backed container database broker. It owns object listing rows, per-storage-policy stats, container metadata/status, shard range persistence, schema migrations, sharding state transitions, misplaced-object discovery, and listing/query behavior. It is the persistence core for container servers and sharding machinery.

## Important APIs, Types, and Functions
- Constants define container DB location and schema semantics: `DATADIR`, record types, shard states (`UNSHARDED`, `SHARDING`, `SHARDED`, `COLLAPSED`), shard state groups, `SHARD_RANGE_KEYS`, and SQL scripts for `policy_stat`, `container_info`, `container_stat`, and triggers.
- `update_new_item_from_existing()` merges incoming object rows against existing rows using data, content-type, and metadata timestamps encoded in `created_at`.
- `merge_shards()` and `sift_shard_ranges()` apply shard-range precedence rules for creation timestamp, metadata timestamp, state timestamp, deleted flag, epoch, reported latch, and tombstone count.
- `ContainerBroker(DatabaseBroker)` is the primary API for container DB creation, querying, updates, replication info, migrations, sharding, root/shard metadata, and shard-range discovery.
- Creation and schema APIs include `create_broker()`, `_initialize()`, `create_object_table()`, `create_policy_stat_table()`, `create_container_info_table()`, and `create_shard_range_table()`.
- Object APIs include `put_object()`, `delete_object()`, `merge_items()`, `remove_objects()`, `list_objects_iter()`, `get_objects()`, `_transform_record()`, and `_record_to_dict()`.
- Info/stat APIs include `get_info()`, `_get_info()`, `_get_alternate_object_stats()`, `get_policy_stats()`, `set_storage_policy_index()`, `reported()`, `empty()`, and reclaim helpers.
- Reconciler APIs include `get_reconciler_sync()`, `update_reconciler_sync()`, and `get_misplaced_since()`.
- Shard APIs include `merge_shard_ranges()`, `get_namespaces()`, `get_shard_ranges()`, `get_own_shard_range()`, `enable_sharding()`, `set_sharding_state()`, `set_sharded_state()`, `get_brokers()`, root metadata properties, and `find_shard_ranges()`.

## Control Flow and Behavior
`ContainerBroker` may represent more than one on-disk DB file during sharding. `_init_db_file` is the legacy path, `db_files` discovers valid files by epoch, `db_file` selects the authoritative newest file unless forced, and `get_brokers()` returns both retiring and fresh brokers during `SHARDING`. State is inferred from file count, filename epoch, own shard range epoch, and presence of other shard ranges.

Object writes flow through `put_record()` inherited from `DatabaseBroker` and later `merge_items()`. `merge_items()` begins an immediate SQLite transaction, fetches existing rows by name in chunks under SQLite argument limits, applies `update_new_item_from_existing()`, deletes superseded rows, inserts new rows, and updates incoming replication sync points. SQL triggers update `policy_stat` counters on insert/delete while prohibiting `UPDATE` of object rows.

Listings in `list_objects_iter()` commit pending puts first, build SQL predicates for markers, end markers, prefix, delimiter, path, reverse order, deletion mode, policy selection, reserved-byte filtering, and row-id bounds. Delimiter handling may iterate and requery to produce pseudo-directory entries while respecting limit.

Shard-range persistence mirrors object merge behavior but uses `merge_shards()` precedence. Query APIs convert rows into `ShardRange` or `Namespace` objects, sort with Swift shard sort keys outside SQLite because the maximum upper bound is represented by an empty string, and optionally fill a trailing gap with a modified own shard range.

Schema compatibility is active and lazy. Missing `storage_policy_index`, `policy_stat`, sync point, shard `reported`, shard `tombstones`, or `shard_range` table errors trigger migrations or compatibility defaults. Legacy `container_stat` is replaced by a view backed by `container_info` and `policy_stat`, with triggers preserving old update behavior.

Sharding state transition in `set_sharding_state()` creates a fresh epoch DB, copies metadata, shard ranges, and sync points, initializes object ROWID continuity with a temporary row, syncs selected container status fields, then atomically renames the fresh DB into place. `set_sharded_state()` unlinks the retiring DB only when a fresher DB is present.

## State and Persistence
Persistence is SQLite files under the container data directory plus `.pending` files inherited from `DatabaseBroker`. Core tables are `object`, `policy_stat`, `container_info`, compatibility view `container_stat`, sync tables from the base broker, and `shard_range`. Triggers maintain object counts, bytes, hashes, and policy stats. Metadata includes sharding sysmeta keys such as `X-Container-Sysmeta-Shard-Root` and quoted root. Cached in-memory state includes db file lists, storage policy index, account/container identity, root account/container, and database version.

## Dependencies and Integration Points
The broker extends `swift.common.db.DatabaseBroker` and uses Swift timestamp encoding, sharding types (`ShardRange`, `ShardRangeList`, `Namespace`), path hashing/storage helpers, DB filename epoch helpers, `tpool` for blocking SQLite merge work, and container listing limits. It integrates with container server request handling, replicator, updater, sharder, reconciler, auditor, and account/stat reporting paths.

## Risks and Edge Cases
- Timestamp merge semantics are subtle: data, content-type, metadata, and swift_bytes must be preserved independently despite sharing columns.
- Lazy migrations happen inside operational paths; migration failures can surface during reads or writes, not only at startup.
- Multi-DB sharding states require careful file selection and `skip_commits` behavior to avoid writing to retiring DBs incorrectly.
- `set_sharding_state()` manipulates ROWID continuity and file renames; partial failures before rename must not leave authoritative state ambiguous.
- Listing delimiter and reverse-marker logic is complex and prone to off-by-one or duplicate pseudo-directory bugs.
- Shard range sorting cannot rely on SQLite due to empty-string max bounds, so Python sort keys must remain consistent with sharding semantics.
- Root-container detection relies on sysmeta and own shard range deletion state, including legacy deleted shard cases.

## Test Signals
Important tests should cover object timestamp merges, swift_bytes extraction/restoration, policy-stat trigger counts, legacy schema migrations, pending put commits before reads, all listing combinations, replication sync updates, misplaced-object queries, shard-range merge precedence, namespace gap filling, DB state transitions, fresh epoch DB creation and retiring DB unlinking, root/shard metadata parsing, and reclaim safety for sharded containers.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/container/backend.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/container/reconciler.py -->
# sources/object-store/openstack-swift/swift/container/reconciler.py

## Purpose
This module implements the container reconciler daemon and helper functions for misplaced object queues. It detects object listings whose storage policy does not match the container's current policy, queues them under `.misplaced_objects`, and later copies/deletes object data so the object lands in the correct policy while cleaning stale source entries.

## Important APIs, Types, and Functions
- `cmp_policy_info()`, `incorrect_policy_index()`, `translate_container_headers_to_info()`, and `best_policy_index()` decide which container policy information is authoritative across primary container responses, accounting for delete/recreate races.
- `get_reconciler_container_name()` buckets queue entries by object metadata timestamp rounded down to an hour.
- `get_reconciler_obj_name()` encodes queue object names as `<policy_index>:/<account>/<container>/<object>`.
- `get_reconciler_content_type()` maps queue operations to `application/x-put` or `application/x-delete`.
- `get_row_to_q_entry_translator()` converts broker misplaced rows into queue object records.
- `add_to_reconciler_queue()` writes queue entries directly to primary container servers and succeeds on majority.
- `parse_raw_obj()` decodes queue listing rows into reconciliation work items.
- `direct_get_container_policy_index()` queries primary container servers and caches majority-derived policy index briefly with `LRUCache`.
- `direct_delete_container_entry()` removes a queue object directly from container servers.
- `ContainerReconciler(Daemon)` owns the daemon config, internal client, queue iteration, object reconciliation, stats, process sharding, and run loop.

## Control Flow and Behavior
Queue insertion computes an hour bucket from the object's metadata timestamp, encodes the source policy and object path into the queue object name, chooses an operation content type, and sends direct PUTs to the misplaced-objects account using the replication network header. The queue entry's etag/hash carries the original object timestamp.

During reconciliation, `ContainerReconciler.reconcile()` iterates the current queue container first, then existing queue containers in reverse listing order. For each raw object it calls `parse_raw_obj()`, optionally filters by configured process modulo hash, and spawns `process_queue_item()` in an eventlet `GreenPool`.

`_reconcile_object()` first determines the container's current policy by direct HEAD majority. If the queue policy already matches, the item is done. It skips reconciliation while either source or destination policy is in part-power-increase state. It then checks destination metadata; if destination has a timestamp newer than or equal to the queue timestamp, the source can be tombstoned. Otherwise it fetches the source object from the queued policy. A queued DELETE with missing source ensures a tombstone in the destination policy; a PUT copies the source object to the destination with a slightly later timestamp and then tombstones the source.

Successful work calls `pop_queue()`, which deletes the queue object using a timestamp later than both queue record and queue object timestamps. Failures leave the queue entry for retry. Old empty queue containers are deleted after `reclaim_age`.

## State and Persistence
Persistent state lives in `.misplaced_objects` account containers and in object/container rings. Queue container names are hourly epoch buckets. Queue object names encode source policy and object path, while content type encodes operation and etag/hash encodes the source timestamp. The daemon holds transient `stats`, `last_stat_time`, config values (`reclaim_age`, `interval`, `concurrency`, `processes`, `process`), and an `InternalClient`.

## Dependencies and Integration Points
The reconciler depends on container rings, object rings via storage policies, `InternalClient`, direct container client operations, `ContainerBroker.get_misplaced_since()` indirectly through queue translation, timestamp utilities, `MISPLACED_OBJECTS_ACCOUNT`, replication network headers, Swift constraints, and daemon runner utilities. It integrates with container updater/reconciler queue producers and object-server policy placement.

## Risks and Edge Cases
- Policy comparison is intentionally nuanced around deleted and recreated containers; incorrect ordering can move objects to stale policies.
- Direct client majority failures cause retries and can delay cleanup.
- Reconciliation is skipped during part-power increase because partition layout is unstable.
- Timestamp offsets (`slightly_later_timestamp`) are critical to avoid overwriting newer user writes while ensuring cleanup tombstones win over stale rows.
- If source data is unavailable until `reclaim_age` expires, the daemon eventually logs critical `lost_source` and drops the queue item as handled.
- Invalid queue object names or content types are logged and skipped, leaving bad records unless separately removed.
- Process modulo filtering must match across multiple daemon processes to avoid duplicate or missed work.

## Test Signals
Tests should cover policy-info comparison for deleted/recreated containers, majority success/failure for queue insertion and policy HEADs, queue name parsing, PUT versus DELETE reconciliation, newer destination handling, missing/old source retry versus expiration, PPI skip behavior, queue popping timestamps, old empty container cleanup, process sharding by hash, stats counters, and exception containment in `reconcile_object()` and `run_once()`.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/container/reconciler.py -->
