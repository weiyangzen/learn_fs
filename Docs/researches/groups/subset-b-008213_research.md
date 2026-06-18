# subset-b-008213 research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/relinker.py -->
# sources/object-store/openstack-swift/swift/cli/relinker.py

## Purpose
`relinker.py` implements `swift-object-relinker`, the operational tool used during object-ring partition-power increases. It runs in two phases: `relink` creates hard links from old partition directories into the next partition-power layout, and `cleanup` removes old files after the ring has been advanced and the new layout is authoritative.

## Important APIs, types, and functions
- Constants define lock/state filenames, phase names, exit codes, and the default recon update interval.
- `policy()` resolves CLI policy names or indexes through `POLICIES`.
- `_aggregate_stats()`, `_aggregate_recon_stats()`, `_zero_stats()`, and `_zero_collated_stats()` shape per-policy, per-device, and worker recon data.
- `Relinker` owns traversal, per-device locking, state-file resume, diskfile operations, recon updates, and final status.
- `Relinker.devices_filter()`, `partitions_filter()`, `hashes_filter()`, and hook methods plug into `audit_location_generator`.
- `Relinker.do_relink()` wraps `diskfile.relink_paths()` and handles hardlink collisions, tombstone special cases, quarantine retry, and cleanup tolerance.
- `Relinker.process_location()` compares old and new hash directories, creates missing required links, removes old files in cleanup mode, and invalidates suffix hashes.
- `parallel_process()` resets recon state, splits devices across forked workers, waits for child exit statuses, and maps failures to tool exit codes.
- `main()` merges config-file and CLI options, sets the eventlet hub, optionally drops privileges, builds the relinker config, and starts `parallel_process()`.

## Control flow
The CLI accepts an `action` of `relink` or `cleanup`, optional object-relinker config, policy/device/partition filters, rate limits, worker count, logging/debug flags, and hardlink-collision policy. `parallel_process()` clears the previous recon file, chooses worker count (`auto` means one worker per device), then either runs one `Relinker` inline or forks workers with evenly distributed device lists.

Each worker iterates selected storage policies. It reloads the object ring and only processes policies whose `next_part_power` state matches the requested phase: during `relink`, `next_part_power` differs from `part_power`; during `cleanup`, the ring has already advanced so they match. For each policy, `audit_location_generator()` walks devices, partitions, suffixes, and hash dirs. Pre-device hooks take an exclusive `.relink.<datadir>.lock`, read `relink.<datadir>.json` if compatible, and initialize recon progress. Partition filtering excludes upper-half partitions that do not need work for the current phase, resumes incomplete partition states, and scans in reverse partition order to reduce unnecessary reads.

For every mismatched hash path, `process_location()` cleans both target and source on-disk file sets, computes the newest required files with the diskfile manager, drops obsolete entries, then ensures every required source file is linked to the target. In cleanup mode, old files are removed only if every required link was verified. Post-partition hooks invalidate affected hashes, opportunistically remove empty old partition directories during cleanup, and atomically persist state by writing and fsyncing a temp JSON file before rename.

## State and persistence behavior
This file mutates object storage paths directly through hard links and deletes. Per-device progress is persisted in `relink.<datadir>.json` so interrupted runs resume partition-by-partition. The lock file serializes work per device/datadir. Recon cache state is periodically dumped to `RECON_RELINKER_FILE`, including worker liveness, per-device policy progress, timestamps, totals, and return codes. Cleanup can delete old object files and empty partitions, while relink may quarantine colliding target files when `clobber_hardlink_collisions` is enabled.

## Dependencies and integration points
The tool depends on Swift storage policies, object rings, `DiskFileRouter`, diskfile hash invalidation/cleanup/linking/quarantine helpers, `audit_location_generator`, rate limiting, recon cache dumping, privilege dropping, logging adapters, eventlet hub setup, and ring partition-path utilities. It is tightly coupled to `swift-ring-builder` partition-power commands: operators prepare the ring, run relink across object servers, increase partition power, deploy the ring, run cleanup, then finish the increase.

## Risks and edge cases
The phase predicates must match ring rollout order; running cleanup before all servers use the advanced ring can remove live old-path data. Hardlink collisions are dangerous because target and source may contain different inodes for the same timestamp; tombstone collisions are tolerated, optional clobbering quarantines target files during relink, and cleanup favors the new location. State-file compatibility checks protect against using stale progress after ring power changes, but corrupt state files are removed and the scan restarts. Hash invalidation failures are logged without counting as hard errors after a link is already created, leaving replication or periodic rehash to recover. Device mount/list errors are aggregated into non-zero exits even if traversal itself logs them as warnings.

## Test signals
Useful tests should cover phase filtering for `part_power`/`next_part_power`, state-file resume and invalidation, per-device locking, partition scan filtering, relink idempotence, cleanup idempotence, hardlink collision modes, tombstone collision tolerance, suffix invalidation failures, unmounted or unlistable devices, worker aggregation, and recon output. Integration tests need realistic object diskfile layouts and ring transition sequencing because correctness depends on filesystem semantics and operational ordering.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/relinker.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/reload.py -->
# sources/object-store/openstack-swift/swift/cli/reload.py

## Purpose
`reload.py` provides a safe CLI for reloading Swift WSGI server managers with minimal client impact. It verifies that a supplied PID is a supported Swift server manager, checks the running command's configuration, sends `SIGUSR1`, and optionally waits for systemd-style readiness notifications.

## Important APIs, types, and functions
- `EXIT_BAD_PID`, `EXIT_RELOAD_FAILED`, and `EXIT_RELOAD_TIMEOUT` encode user, reload, and wait failures.
- `validate_manager_pid(pid)` reads `/proc/<pid>/cmdline`, checks the session id, validates that exactly one non-Python `swift-*` script is present, and rejects unsupported processes or worker PIDs.
- `main(args=None)` defines CLI parsing, calls config validation through `subprocess.check_call(cmd + ["--test-config"])`, sends `SIGUSR1`, and waits on `NotificationServer` unless `--no-wait` is used.

## Control flow
The command requires a PID and accepts either a numeric timeout or `--no-wait`, plus verbose output. PID validation fails with exit code 2 when `/proc` data is unavailable, the process is not a Swift WSGI server, the server type lacks config-check support, or the process is a worker rather than the manager session leader. After validation, the original process command line is reused with `--test-config`; any non-zero result aborts before signaling. In wait mode, `NotificationServer` is bound before `SIGUSR1` is sent so reload notifications are not missed. The loop reads newline-delimited notification records until `READY=1`; timeout maps to `128 + ETIMEDOUT`. In no-wait mode, the signal is sent and success is printed immediately.

## State and persistence behavior
The file does not persist Swift data. It observes Linux `/proc`, process sessions, and notification sockets, and it mutates process state by sending `SIGUSR1` to the manager. The config test may read service config and fail without changing the running process. Output and exit codes are the durable operational contract for automation.

## Dependencies and integration points
It depends on Linux `/proc`, POSIX process sessions/signals, `subprocess`, sockets, and `swift.common.utils.NotificationServer`. It integrates with server manager processes that understand `--test-config`, `SIGUSR1` seamless reload, and `READY=1`/`RELOADING=1`/`STOPPING=1` notifications.

## Risks and edge cases
The process detector assumes command-line entries include a `/bin/` Swift script and that the manager is its own session leader; unusual packaging or launch wrappers may be rejected. There is no fallback for non-Linux systems without `/proc`. Reusing the original command with `--test-config` can fail if the command line included flags that do not compose with the test option. If the notification socket cannot bind, the tool exits failed before signaling; if the process never emits `READY=1`, reload may have happened but the CLI reports timeout.

## Test signals
Tests should mock `/proc` reads, `os.getsid`, `subprocess.check_call`, `NotificationServer`, `os.kill`, socket timeout, and OSError binding failures. Important cases include worker PID rejection, unsupported script rejection, config-test failure before signal, `--no-wait` behavior, verbose notification output, and timeout exit code.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/reload.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/ring_builder_analyzer.py -->
# sources/object-store/openstack-swift/swift/cli/ring_builder_analyzer.py

## Purpose
`ring_builder_analyzer.py` is a developer tool for replaying JSON ring-builder scenarios and measuring rebalance behavior after staged topology changes. It helps quantify ring-builder improvements or regressions by applying scripted add/remove/weight/save commands and printing rebalance convergence metrics per round.

## Important APIs, types, and functions
- `ARG_PARSER` defines `--check` and the scenario file argument.
- `ParseCommandError` decorates validation failures with round and command indexes.
- `_parse_weight()`, `_parse_add_command()`, `_parse_remove_command()`, `_parse_set_weight_command()`, and `_parse_save_command()` validate and normalize scenario commands.
- `parse_scenario(scenario_data)` validates top-level JSON fields (`part_power`, `replicas`, `overload`, `random_seed`, `rounds`) and returns a parsed scenario structure.
- `run_scenario(scenario)` creates a `RingBuilder`, applies each round, repeatedly rebalances with the configured seed, pretends min-part-hours passed between iterations, and prints moved parts, balance, and removed-device counts.
- `main(argv=None)` reads the scenario file, validates it, optionally runs it, and returns a shell status.

## Control flow
Scenario parsing first loads JSON and rejects non-object input. Required numeric fields are type-converted and range-checked: partition power must be 1 through 32, replicas at least 1, overload non-negative, and random seed an integer. Each round must be a list, and each command is dispatched by its first element. Add commands parse Swift ring device strings with `parse_add_value`, default absent regions to 1, default replication IP/port to normal IP/port, and attach a non-negative weight. Remove and set-weight commands parse integer device IDs; save passes a file path through to the builder.

Execution builds `builder.RingBuilder(part_power, replicas, 1)`, applies overload, maps parsed command names to builder methods, and mutates each command list by popping the command name before invocation. After a round, the tool rebalances at least once, advances min-part-hours, then keeps rebalancing until no parts/removed devices change or balance movement is less than one point, except for `MAX_BALANCE` special cases.

## State and persistence behavior
Most state is in-memory `RingBuilder` mutation. The `save` scenario command may persist builder files via `RingBuilder.save`. The scenario list itself is destructively mutated by `run_scenario()` because it pops command names; callers should not reuse the same parsed scenario for repeated runs.

## Dependencies and integration points
The analyzer depends on JSON scenarios, `swift.common.ring.builder.RingBuilder`, `builder.MAX_BALANCE`, and `swift.common.ring.utils.parse_add_value`. It is an offline diagnostic tool rather than a production daemon, but it exercises the same ring-builder algorithms operators use for device changes and rebalances.

## Risks and edge cases
Command validation assumes each command is indexable and non-empty before reading `command[0]`; malformed empty commands can raise a generic exception rather than a `ParseCommandError`. The destructive pop in `run_scenario()` is surprising and makes repeated execution of the same parsed object invalid. The stop condition is heuristic and intended for analysis, not for authoritative ring validation. `save` commands allow scenario files to write paths chosen by the scenario author.

## Test signals
Focused tests should cover JSON validation errors, add parsing defaults, negative weights, unknown commands, empty/malformed command arrays, `--check` behavior, deterministic rebalance output with a seed, `save` dispatch, and whether repeated `run_scenario()` calls on the same object fail due to mutation.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/ring_builder_analyzer.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/ringbuilder.py -->
# sources/object-store/openstack-swift/swift/cli/ringbuilder.py

## Purpose
`ringbuilder.py` implements the `swift-ring-builder` CLI for creating, inspecting, modifying, rebalancing, validating, and serializing Swift ring builder files and distributable ring files. It is the primary operator interface for account, container, object, and composite-adjacent ring lifecycle work, including partition-power increase coordination for object rings.

## Important APIs, types, and functions
- Global version/exit constants define CLI status behavior: success 0, warning 1, error 2.
- `format_device()` produces stable human-readable device descriptions with IPv6 bracket handling.
- Parser helpers (`_parse_search_values`, `_parse_list_parts_values`, `_parse_add_values`, `_parse_set_*_values`, `_parse_remove_values`) normalize old-style device strings and new option-style inputs.
- `check_devs()` guards multi-device destructive changes with interactive confirmation unless `--yes` is supplied.
- `_set_weight_values()`, `_set_region_values()`, `_set_zone_values()`, and `_set_info_values()` mutate device dictionaries through `RingBuilder` APIs or direct metadata updates after duplicate checks.
- `_make_display_device_table()` builds aligned device table printers for default output.
- `Commands` is a static-method command table for `create`, default display, `version`, `search`, `list_parts`, `add`, `set_weight`, `set_region`, `set_zone`, `set_info`, `remove`, `rebalance`, `dispersion`, `validate`, `write_ring`, `write_builder`, `pretend_min_part_hours_passed`, `set_min_part_hours`, `set_replicas`, `set_overload`, and partition-power commands.
- `main(arguments=None)` maps ring/builder filenames, loads builders, creates backups dir, optionally locks the parent directory for `-safe` invocations, and dispatches commands.
- `error_handling_main()` installs an excepthook so uncaught exceptions print a traceback and exit with status 2.

## Control flow
Startup parses the builder/ring filename pair with `parse_builder_ring_filename_args`, loads a `RingBuilder` except for `create`, `write_builder`, or `version`, and warns if a ring file path was translated to a builder path. It creates a sibling `backups` directory. With no command it displays global ring state, ring-file freshness, device balance table, and partition-power progress instructions.

Device commands parse search or add syntax through `swift.common.ring.utils`, confirm broad matches, mutate the builder, and save the builder file. Adds and removes are blocked while partition-power increase is in progress. `set_info` directly changes IP/port/device/meta fields after checking no other device already uses the target endpoint/device tuple; it does not itself require rebalance, though `write_ring` may be needed.

`rebalance` parses force, seed, debug, and ring format options. It refuses to run while partition-power increase is active, captures pre-rebalance balance/dispersion, calls `builder.rebalance()`, handles min-part-hours and empty-ring errors, rejects low-impact saves unless forced or device metadata changed, validates the result, prints balance/dispersion warnings, then saves timestamped backups plus current `.ring.gz` and builder files. `write_ring` serializes current ring data without a rebalance and warns when writing a ring with devices but no assignments. `write_builder` reconstructs a lossy builder from a ring file.

Partition-power commands enforce object-ring-only preparation, transition `next_part_power` through prepare, increase, cancel, and finish states, and print explicit operational instructions to run `swift-object-relinker` between ring deployment steps. `dispersion` can recalculate and save cached dispersion data, prints graph rows, and exits warning when placement is imperfect.

## State and persistence behavior
The command mutates builder files, distributable ring files, and backup files under `backups/`. `rebalance` and `write_ring` write ring data with a selected serialization format. Device changes update persistent device dictionaries and builder version state. `write_builder` can create a new builder from existing ring data, but loses some original builder metadata such as exact min-part-hours unless supplied. Safe-mode invocations lock the builder parent directory for 15 seconds to avoid concurrent writes.

## Dependencies and integration points
The CLI is a thin but broad integration layer over `RingBuilder`, `Ring`, `RingData`, `CompositeRingBuilder` detection, ring serialization codecs, ring utility parsers, dispersion reporting, validation exceptions, parent-directory locks, and IPv6 validation. Operators use its outputs and exit codes in ring deployment automation. Its partition-power commands are coupled to `swift-object-relinker` and object server rollout order.

## Risks and edge cases
The module relies on global `argv`, `builder`, `builder_file`, `ring_file`, and `backup_dir`, making command methods hard to compose and sensitive to tests that do not reset globals. Many helpers call `exit()` directly, so library-style callers cannot recover cleanly. Interactive confirmation can block automation unless `--yes` is used. Direct device-dict mutation in `set_info` must stay compatible with builder invariants. Rebalance save refusal is intentionally conservative and may surprise users after small improvements. Partition-power commands can affect data availability if rings are deployed before relink/cleanup steps complete.

## Test signals
Important tests should cover both old and new command syntax, IPv6 formatting, duplicate device detection, interactive abort and `--yes`, empty and invalid builder handling, rebalance warning/error/save thresholds, ring format option behavior, backup creation, safe-mode locking, partition-power command sequencing, lossy `write_builder`, and exception-to-exit-code mapping in `error_handling_main()`.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/ringbuilder.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/ringcomposer.py -->
# sources/object-store/openstack-swift/swift/cli/ringcomposer.py

## Purpose
`ringcomposer.py` implements the experimental `swift-ring-composer` CLI for creating composite ring files from multiple component ring builder files. It can display composite builder metadata or compose and write a composite ring plus its composite builder metadata file.

## Important APIs, types, and functions
- `EXIT_SUCCESS` and `EXIT_ERROR` define CLI statuses.
- `WARNING` and `DESCRIPTION` contain operator-facing experimental-tool text.
- `_print_to_stderr()` and `_print_err()` centralize error output.
- `show(composite_builder, args)` prints the loaded composite builder as sorted, indented JSON.
- `compose(composite_builder, args)` creates or reuses a `CompositeRingBuilder`, calls `compose(builder_files, force=args.force, require_modified=True)`, saves the ring data to `--output`, then saves the composite builder file.
- `main(arguments=None)` parses the composite builder file plus `show` or `compose`, loads existing metadata when required, and exits with the subcommand status.

## Control flow
The CLI always prints the experimental warning to stderr before parsing arguments. `show` requires an existing composite builder file, loads it, and dumps metadata. `compose` permits a missing composite builder file by creating a fresh `CompositeRingBuilder`, then requires `--output` and accepts zero or more builder files plus `--force`. Composition, ring save, and builder save are separate try blocks so failure messages identify which stage failed.

## State and persistence behavior
`show` is read-only. `compose` writes two artifacts: the composed ring file at `args.output` and the composite builder metadata file at `args.composite_builder_file`. With `require_modified=True`, composition can refuse to rewrite an unchanged composite unless `--force` is appropriate at the `CompositeRingBuilder` layer.

## Dependencies and integration points
The file depends almost entirely on `swift.common.ring.composite_builder.CompositeRingBuilder` and ring data serialization returned by its `compose()` method. It complements but is distinct from `swift-ring-builder`; the docstring explicitly warns that generated composite rings do not have a normal builder file and should not be managed through a reconstructed temporary builder.

## Risks and edge cases
The code uses broad `except Exception` handlers to convert all compose/load/save failures into status 2, which is useful operationally but hides exception type detail. `main()` assumes a subparser sets `args.func`; invoking without a subcommand depends on argparse behavior and may produce a less curated error. Empty `builder_files` is syntactically allowed and delegated to `CompositeRingBuilder.compose()` for validation. The tool is explicitly experimental, so CLI and behavior may be unstable.

## Test signals
Tests should exercise missing and existing composite builder files, `show` JSON output, compose success write order, load/compose/ring-save/builder-save failures, `--force` propagation, no-subcommand parser behavior, and the exit status contract.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/ringcomposer.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/shard-info.py -->
# sources/object-store/openstack-swift/swift/cli/shard-info.py

## Purpose
`shard-info.py` is an operator diagnostic script that scans local container databases and prints sharding topology details grouped by root container and shard containers. It reports DB locations, node placement, database state, object/byte counts, sharding sysmeta, own shard ranges, and referenced shard ranges.

## Important APIs, types, and functions
- `broker_key(broker)` loads broker info and uses `broker.path` as the container identity key.
- `container_type(broker)` classifies brokers as `ROOT` or `SHARD`.
- `collect_brokers(conf_path, names2nodes)` reads a container-replicator config, loads the container ring, scans local container DB datadirs, builds `ContainerBroker` instances, and indexes them by container name and node id/index.
- `print_broker_info()`, `print_db()`, `print_own_shard_range()`, `print_shard_range()`, and related helpers produce formatted diagnostic output.
- `print_container()` recursively prints a root or shard container and follows shard range names, avoiding cycles through `used_names`.
- `run(conf_paths)` collects brokers from multiple configs and prints root containers with their shards.

## Control flow
When executed directly, the script lists `/etc/swift/container-server` entries ending in `conf` or `conf.d` and passes those paths to `run()`. Each config is read from its `container-replicator` section to find devices and `swift_dir`. For each container-ring device with a local datadir, `roundrobin_datadirs()` yields DB files. The script creates a `ContainerBroker`, maps the on-disk partition to a primary node index or `handoff`, and stores the broker under its path identity.

Printing starts with root containers detected by any broker reporting `is_root_container()`. For a container, it prints all DB files ordered by node index, flags type mismatches against the expected root/shard type, prints replicated info and raw object count, prints sharding sysmeta, own shard ranges, all shard ranges, and recursively prints each referenced shard container as expected type `SHARD`.

## State and persistence behavior
The script is intended to be read-only. It opens SQLite-backed container brokers and calls broker getters but does not write to DBs. It depends on local device directory state and ring files. The only process state is the recursive `used_names` set that prevents duplicate detail output and cycles.

## Dependencies and integration points
It integrates with container-replicator configuration, the container ring, `roundrobin_datadirs()`, `ContainerBroker`, container sharding metadata, and Swift `Timestamp` formatting. It is useful when debugging container-sharder behavior, misplaced DBs, handoff DBs, or inconsistent shard-range state across replicas.

## Risks and edge cases
There is no argparse or error handling around missing `/etc/swift/container-server`, bad configs, missing rings, corrupt DBs, or absent referenced shard brokers; diagnostics may crash instead of partially reporting. `collect_brokers()` creates a local `brokers` variable that is never populated or used as the return value, so all useful data flows through the passed `names2nodes` defaultdict. The script shadows the built-in name `range` in print helpers. Recursive printing assumes shard range names exist in the collected map; missing local shard DBs can raise a `KeyError`.

## Test signals
Tests should use fake rings, configs, `roundrobin_datadirs()` output, and `ContainerBroker` doubles to cover primary versus handoff node indexing, root/shard type mismatch output, deleted shard range ordering, recursion cycle prevention, missing shard names, multiple config paths, and formatting of delete timestamps and epoch values.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/cli/shard-info.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/__init__.py -->
# sources/object-store/openstack-swift/swift/common/__init__.py

## Purpose
`swift/common/__init__.py` marks `swift.common` as a package and contains a single module docstring: “Code common to all of Swift.” It does not define runtime APIs.

## Important APIs, types, and functions
There are no constants, classes, functions, imports, or side effects. The file's only content is the package docstring.

## Control flow
No executable control flow exists beyond Python package import mechanics.

## State and persistence behavior
The file maintains no state and performs no persistence. Its presence enables imports such as `swift.common.constraints`, `swift.common.daemon`, and `swift.common.db`.

## Dependencies and integration points
It is the package root for shared Swift modules. Integration is structural rather than behavioral.

## Risks and edge cases
Risk is minimal. Removing or renaming it could affect package discovery depending on Python packaging mode, but its contents are otherwise inert.

## Test signals
No dedicated unit tests are needed beyond import/package discovery coverage from the broader Swift test suite.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/base_storage_server.py -->
# sources/object-store/openstack-swift/swift/common/base_storage_server.py

## Purpose
`base_storage_server.py` contains shared behavior for Swift storage server controllers. It provides timing decorators for public request handlers and a base class implementing the common `OPTIONS` response for object, account, and container servers.

## Important APIs, types, and functions
- `labeled_timing_stats(metric, **dec_kwargs)` returns a decorator that passes a mutable `timing_stats_labels` dict into a controller method, captures `HTTPException` as a response, adds method/status labels, and emits `statsd.timing_since()`.
- `timing_stats(**dec_kwargs)` returns a decorator that records normal timings or `.errors.timing` based on whether the response status is a server error.
- `BaseStorageServer.__init__()` stores replication-server enablement and log anonymization settings from config.
- `BaseStorageServer.server_type` is an abstract property expected to be implemented by concrete storage servers.
- `BaseStorageServer.allowed_methods` introspects callable attributes marked `publicly_accessible`, excluding replication methods when `replication_server` is disabled.
- `BaseStorageServer.OPTIONS()` is a public timed handler returning `Allow` and `Server` headers.

## Control flow
Decorated controller methods are invoked inside wrappers that record start time, catch `HTTPException`, derive status from the returned/raised response, and emit metrics before returning the response object. `allowed_methods` lazily scans the controller once, filtering on attributes attached by Swift's `@public` decorator and optional `replication` marker, then caches a sorted method list. `OPTIONS` builds a `swob.Response` with the allowed methods and `server_type/swift_version`.

## State and persistence behavior
State is in-memory configuration and the cached `_allowed_methods` list. There is no disk persistence. Metrics are emitted externally through the controller logger or statsd client, and the response exposes Swift version and allowed API surface.

## Dependencies and integration points
The module depends on Swift version metadata, `public`, `config_true_value`, `LOG_LINE_DEFAULT_FORMAT`, server-error classification, and `swob` response/exception types. Concrete account, container, and object server controllers inherit the base class or use the decorators for timing behavior.

## Risks and edge cases
`labeled_timing_stats` reserves `method` and `status` labels; controller-provided labels with those names are overwritten. The decorator assumes the wrapped method accepts `timing_stats_labels`; applying it to a method without that keyword will break. `allowed_methods` caches results, so dynamic changes to public/replication attributes after first access are not reflected. `timing_stats` treats non-server HTTP errors as normal timings, matching Swift's metric convention but requiring careful interpretation.

## Test signals
Tests should cover public method discovery, replication method suppression, `OPTIONS` headers, timing/error metric names for 2xx/4xx/5xx responses, raised `HTTPException` handling, and labeled timing label overwrite behavior.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/base_storage_server.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/bufferedhttp.py -->
# sources/object-store/openstack-swift/swift/common/bufferedhttp.py

## Purpose
`bufferedhttp.py` provides backend HTTP client helpers optimized for Swift's many small inter-server requests. It subclasses eventlet-green HTTP response/connection classes to buffer header reads, support `100-continue`, set TCP_NODELAY, quote Swift backend paths, and normalize query strings.

## Important APIs, types, and functions
- Module initialization raises `http.client._MAXHEADERS` and eventlet green HTTP max headers to match Swift's constraint-derived header count with slack.
- `BufferedHTTPResponse` wraps a green socket, exposes a `headers` property that repairs a Python header parsing payload issue, supports `expect_response()`, handles buffered line reads in `read()`, and can hard-close the underlying real socket with `nuke_from_orbit()`.
- `BufferedHTTPConnection` sets `response_class`, records method/path, sets TCP_NODELAY after connect, encodes header names to latin-1 bytes, supports `getexpect()`, and logs response latency in `getresponse()`.
- `http_connect()` builds a backend path from device, partition, and object/account/container path, then delegates to `http_connect_raw()`.
- `http_connect_raw()` chooses `HTTPSConnection` or `BufferedHTTPConnection`, appends a normalized query string, sends request line and headers, and returns the open connection.

## Control flow
`http_connect()` ensures path/device/partition values are bytes, quotes `/<device>/<partition><path>`, and passes the encoded backend path onward. `http_connect_raw()` fills a default port, constructs the correct connection class, round-trips query strings through `parse_qsl()` and `urlencode()` with latin-1 handling, sends the request with `skip_host` when a Host header is supplied, writes all headers as strings, and calls `endheaders()` without sending a body.

`BufferedHTTPResponse.expect_response()` closes any existing file object, reopens an unbuffered reader, reads the status line, and either parses headers for `100 Continue` or stashes a lambda so later `begin()` sees the already-read non-continue status. The custom `headers` setter handles cases where parsed header payload lines were left in the message body by adding valid `Header: value` lines back to the header mapping and clearing the payload.

## State and persistence behavior
State is per-connection and per-response: sockets, file objects, method/path metadata, timing, buffered bytes, header objects, and underlying real socket references. No persistent storage is touched. The module does mutate global stdlib/eventlet header limits at import time.

## Dependencies and integration points
It depends on Swift constraints, eventlet green HTTP classes exported by `swift.common.concurrency`, Python `http.client`, socket options, urllib quoting/parsing, and logging. It is used by backend replication, updater, auditor, proxy, and storage components that make internal Swift HTTP requests to devices and partitions.

## Risks and edge cases
Import-time mutation of `_MAXHEADERS` relies on private stdlib/eventlet attributes. `nuke_from_orbit()` calls `_real_close()` on the underlying socket, a private low-level method. Header payload repair intentionally stops on malformed or folded lines and does not attempt full RFC folding support. Path/query encoding must preserve Swift's byte semantics; changing latin-1 handling can break object names or query parameters. `getresponse()` assumes `_connected_time`, `_method`, and `_path` were set by this connection's methods.

## Test signals
Tests should cover quoted backend paths for bytes/str/int partitions, query-string normalization with blank values, Host header skip behavior, header-name byte encoding, `100 Continue` and non-continue paths, buffered reads with `amt`, socket close/nuke behavior, TCP_NODELAY setup, header payload repair, and import-time max-header alignment with constraints.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/bufferedhttp.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/concurrency.py -->
# sources/object-store/openstack-swift/swift/common/concurrency.py

## Purpose
`concurrency.py` centralizes Swift's eventlet imports and re-exports. It gives the rest of Swift one stable module from which to import green sockets, queues, pools, HTTP classes, timeouts, monkey patching, and related eventlet primitives instead of importing directly from eventlet.

## Important APIs, types, and functions
- Re-exported modules include `eventlet`, `debug`, `greenio`, `greenthread`, `hubs`, `patcher`, `queue`, `tpool`, `wsgi`, `websocket`, and green stdlib modules.
- Re-exported classes/functions include `GreenPile`, `GreenPool`, `Timeout`, `Event`, `listen`, `sleep`, `spawn`, `spawn_n`, `getcurrent`, `trampoline`, `Pool`, `LightQueue`, `Queue`, `Semaphore`, and `GreenletExit`.
- HTTP-specific exports include `CONTINUE`, `HTTPConnection`, `HTTPResponse`, `HTTPSConnection`, `ImproperConnectionState`, `_UNKNOWN`, and `green_http_client`.
- Aliases expose `hub_exceptions`, `hub_prevent_multiple_readers`, `monkey_patch`, `shutdown_safe`, and `ChunkReadError`.
- `__all__` documents and constrains the intended public re-export set.

## Control flow
There is no dynamic control flow beyond importing eventlet modules and binding aliases. Importers use this module as the compatibility boundary for eventlet API access.

## State and persistence behavior
The module holds references to eventlet objects and functions. It does not persist data. Importing it may load eventlet modules and their global state, but this file itself does not monkey-patch or configure hubs.

## Dependencies and integration points
This file depends entirely on eventlet and eventlet's green standard-library shims. It is imported by modules such as `bufferedhttp.py`, `daemon.py`, `db.py`, `db_auditor.py`, and `relinker.py` for timeouts, sleep, HTTP classes, and hub behavior.

## Risks and edge cases
The module is a compatibility choke point: eventlet API removals or relocations can break many Swift modules at import time. `_UNKNOWN` is a private HTTP-client sentinel re-exported for compatibility. The duplicate `greenio` entry in `__all__` is harmless but illustrates that this is a manual list. Because imports happen eagerly, environments without eventlet cannot import most Swift common modules that depend on this file.

## Test signals
Tests mainly need import/export coverage: expected names should be importable from `swift.common.concurrency`, aliases should match eventlet functions/classes, and modules that consume the exports should not import eventlet directly for covered primitives. Version-compatibility tests are valuable when upgrading eventlet.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/concurrency.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/constraints.py -->
# sources/object-store/openstack-swift/swift/common/constraints.py

## Purpose
`constraints.py` defines Swift request and metadata limits, loads deployer overrides from `swift.conf`, and provides validation helpers for object creation, metadata headers, drive/mount paths, delete scheduling headers, UTF-8 safety, account/container name formatting, timestamps, and API versions.

## Important APIs, types, and functions
- Module constants define default max file size, metadata name/value/count/overall limits, header and request-line limits, object/account/container name limits, listing limits, valid API versions, extra header allowance, and auto-create account prefix.
- `DEFAULT_CONSTRAINTS`, `OVERRIDE_CONSTRAINTS`, and `EFFECTIVE_CONSTRAINTS` track default, configured, and active values.
- `reload_constraints()` reads `utils.SWIFT_CONF_FILE` section `swift-constraints`, converts values based on default types, updates globals, and populates effective constraints.
- `MAX_HEADER_COUNT` is derived from metadata count, Swift internal/default headers, and extra header count.
- `check_metadata(req, target_type)` validates metadata header names, values, count, aggregate size, header value length, and UTF-8 constraints for account/container metadata.
- `check_object_creation(req, object_name)` validates message length, content length or chunked transfer, object name length, content type, delete headers, content-type UTF-8, and object metadata.
- `check_dir()`, `check_mount()`, and `check_drive()` validate device names and mount/directory existence.
- `valid_timestamp()`, `check_delete_headers()`, `check_utf8()`, `check_name_format()`, and `valid_api_version()` are shared request validation helpers.

## Control flow
At import time `reload_constraints()` applies config overrides and updates module-level uppercase names. Metadata validation iterates every header, first rejecting overlong string header values, then checking only the `x-<target>-meta-` prefix for metadata-specific limits. Object creation reads `req.message_length()`, maps malformed length/transfer-encoding problems to HTTP exceptions, enforces object size and content-type requirements, normalizes delete scheduling headers, and delegates metadata validation.

Drive validation rejects names whose URL-quoted form differs, then requires either `utils.ismount(path)` or `isdir(path)` depending on mount-check mode. Delete-header validation converts `X-Delete-After` to `X-Delete-At`, normalizes timestamps, and rejects past deletion times except backend replication requests. UTF-8 validation accepts strings or bytes that round-trip as UTF-8, rejects surrogate code points, rejects null bytes unless Swift's reserved-byte setting differs, and rejects Swift's reserved byte unless `internal=True`.

## State and persistence behavior
The module has process-global mutable constraint state. Reloading constraints changes module constants that other modules may have imported by value or may read dynamically. Request validation mutates the request headers when `X-Delete-After` is converted to `X-Delete-At`. No persistent storage is written.

## Dependencies and integration points
It integrates with `swift.common.utils` for config path, CSV parsing, mount detection, timestamp normalization, reserved byte, and boolean parsing; with Swift exceptions for invalid timestamps; and with `swob` HTTP exceptions and WSGI string/byte conversion. Proxy, account, container, object, and backend code rely on these helpers before accepting user and internal requests. `bufferedhttp.py` uses `MAX_HEADER_COUNT` to adjust parser limits.

## Risks and edge cases
Import-time config loading means tests and services must call `reload_constraints()` after changing `SWIFT_CONF_FILE`. `MAX_HEADER_COUNT` is computed after import and may not update if constraints are reloaded with a different metadata count or extra header count unless code recomputes it separately. Metadata UTF-8 rules differ by target type: object metadata can contain values that account/container metadata would reject. `check_object_creation()` mutates delete headers, so callers should not expect the original `X-Delete-After` header to remain. `check_utf8('')` returns false, which is correct for names but can surprise generic callers.

## Test signals
Tests should cover config overrides and type conversion, missing/invalid config sections, metadata limit boundaries, header value length, account/container UTF-8 rejection, object creation length and transfer-encoding errors, delete-after/delete-at normalization and replication exception, drive name quoting and mount checks, UTF-8 surrogate/null/reserved-byte behavior, account/container slash rejection, and API-version list coercion.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/constraints.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/container_sync_realms.py -->
# sources/object-store/openstack-swift/swift/common/container_sync_realms.py

## Purpose
`container_sync_realms.py` loads `container-sync-realms.conf` and exposes realm keys, secondary keys, cluster endpoints, cluster lists, and request signatures for Swift container sync. It periodically reloads the config based on file modification time to allow key and endpoint changes without process restart.

## Important APIs, types, and functions
- `ContainerSyncRealms.__init__(conf_path, logger)` initializes reload timers, mtime tracking, data storage, and forces an initial reload.
- `reload()` resets mtime state and delegates to `_reload()`.
- `_reload()` checks mtime no more often than `mtime_check_interval`, parses the config, updates reload interval, and rebuilds uppercase realm/cluster mappings.
- `realms()`, `key()`, `key2()`, `clusters()`, and `endpoint()` are lookup methods that refresh if needed before returning data.
- `get_sig(request_method, path, x_timestamp, nonce, realm_key, user_key)` creates the HMAC-SHA1 hex signature over method, path, timestamp, nonce, and user key using the realm key.

## Control flow
Lookup methods call `_reload()`, which only stats the file when the next mtime-check deadline has passed. Missing files are logged at debug level; other stat errors and parse errors are logged as errors. When mtime changes, the config is read, `DEFAULT/mtime_check_interval` is optionally parsed, and each section becomes an uppercase realm. Options named `key` or `key2` become realm secrets; options beginning `cluster_` become uppercase cluster names mapped to endpoint URLs.

Signature generation coerces nonce and keys to valid UTF-8 strings, encodes path if it is a Python string, then computes an HMAC using a newline-joined byte payload and SHA1.

## State and persistence behavior
State is in-memory: config path, next check time, mtime interval, last mtime, and parsed realm data. The file reads configuration from disk but does not write. Key rotation is supported by reloading both primary and secondary keys when the config mtime changes.

## Dependencies and integration points
It depends on `configparser`, filesystem mtime, logging, `hmac`/`hashlib`, and `get_valid_utf8_str`. Container sync middleware and daemons use it to discover allowed remote realms/clusters and to validate or generate sync signatures.

## Risks and edge cases
If config parsing fails after a previous successful load, old data remains in memory because `self.data` is only replaced after successful parsing. That is resilient but can delay key revocation. The reload interval is itself read from the file, so an invalid interval logs an error and leaves current data behavior dependent on the surrounding parse branch. Cluster and realm names are case-normalized to uppercase, while endpoint values are not normalized. SHA1 HMAC remains the protocol contract; changing it would break compatibility.

## Test signals
Tests should cover missing file logging, mtime-based reload suppression, forced reload, parse errors preserving prior data, interval parsing, uppercase realm/cluster lookup, key/key2 lookup, endpoint lookup, signature byte construction for str and bytes paths, and UTF-8 coercion of nonce and keys.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/container_sync_realms.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/daemon.py -->
# sources/object-store/openstack-swift/swift/common/daemon.py

## Purpose
`daemon.py` defines Swift's base daemon abstraction, the strategy for running a daemon inline or as multiple forked workers, and `run_daemon()` for loading config, preparing process environment, and starting daemon classes. It separates daemon business logic from process-management mechanics.

## Important APIs, types, and functions
- `Daemon` provides `run_once()`, `run_forever()`, `run(once=False)`, `post_multiprocess_run()`, `get_worker_args()`, and `is_healthy()` extension points.
- `DaemonStrategy` handles setup, signal behavior, inline execution, forking, worker tracking, worker restart, health-triggered worker replacement, and cleanup.
- `DaemonStrategy.setup()` validates config, drops privileges, cleans daemon hygiene, captures stdio, installs a SIGTERM handler that kills the process group, and sends systemd readiness notification.
- `run_daemon(klass, conf_file, section_name='', once=False, **kwargs)` derives the config section, reads config, monkey-patches eventlet, configures the hub/logger/priority/fallocate/debug/TZ environment, creates the daemon, and runs it through `DaemonStrategy`.

## Control flow
Subclasses implement `run_once()` and `run_forever()`. If a subclass returns no worker argument dictionaries from `get_worker_args()`, `DaemonStrategy` runs the daemon inline. If worker args are returned, it forks one process per option set, resets SIGHUP/SIGTERM and `NOTIFY_SOCKET` in children, and calls `daemon.run(once, **kwargs)`. The parent periodically asks whether the daemon is healthy, cleans up and respawns workers if not, reaps exited workers, respawns them in forever mode, and exits once all once-mode workers finish.

`run_daemon()` turns class names such as `ObjectReplicator` into section names such as `object-replicator` when none is supplied. It uses command-line `once` or `daemonize=false` to select once mode, configures logging and process priority, supports disabling fallocate, sets eventlet hub exception reporting, pins timezone to UTC, logs start/exit, and returns the daemon instance.

## State and persistence behavior
The strategy tracks worker PIDs and their option dictionaries in memory. It mutates process-level state: user privileges, stdio, signal handlers, process group behavior, eventlet monkey patching/hub selection, priority, fallocate settings, environment variables, and systemd notifications. It does not persist files directly.

## Dependencies and integration points
The module depends on Swift utilities for config reading, logging, privilege dropping, stdio capture, monkey patching, hub selection, priority, fallocate configuration, and systemd notifications. All long-running Swift service daemons can use `run_daemon()` as their entrypoint and inherit `Daemon` for run-once/run-forever behavior.

## Risks and edge cases
The SIGTERM handler sends SIGTERM to process group 0 and exits with `os._exit(0)`, so embedding this strategy in a larger process group would be dangerous. Forked children call `os._exit(0)` to avoid parent cleanup stacks, which is intentional but unforgiving. `register_worker_exit()` appends options for respawn even during cleanup; cleanup then leaves options in `unspawned_worker_options`, which is acceptable because the strategy is stopping. Health checks happen every five seconds by default, so worker option changes are not instantaneous. Eventlet monkey patching occurs inside `run_daemon()` and affects the whole process.

## Test signals
Tests should cover section-name derivation, config read errors, once versus daemonize selection, inline fallback, multi-worker fork/reap/respawn behavior, health-triggered cleanup, SIGTERM handling, child environment reset, systemd notifications, priority/fallocate/eventlet-debug configuration, and `post_multiprocess_run()` invocation after worker completion.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/daemon.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/db.py -->
# sources/object-store/openstack-swift/swift/common/db.py

## Purpose
`db.py` provides Swift's shared SQLite broker infrastructure for account and container databases. It supplies eventlet-friendly SQLite connections, database creation and connection setup, pending-file batching, metadata management, replication sync points, tombstone reclamation, deletion state helpers, quarantine behavior, and common broker extension points.

## Important APIs, types, and functions
- Global settings control DB preallocation, query logging, broker timeout, pickle protocol, pending-file cap, SQLite argument limit, and reclaim page size.
- `native_str_keys_and_values()`, `zero_like()`, `dict_factory()`, and `chexor()` are shared data helpers.
- `_db_timeout()` retries locked SQLite operations under `LockTimeout` with eventlet sleeps and exponential backoff.
- `DatabaseConnectionError` and `DatabaseAlreadyExists` provide contextual SQLite errors.
- `GreenDBConnection` and `GreenDBCursor` wrap SQLite operations so `execute()` and `commit()` cooperate with eventlet during lock waits.
- `get_db_connection()` opens a configured SQLite connection, detects accidental empty DB creation, sets pragmas, row/text factories, trace logging, and the SQL `chexor` function.
- `TombstoneReclaimer` deletes old tombstones in bounded name-ordered batches and reports remaining newer tombstones.
- `DatabaseBroker` is the core base class for account/container brokers, with extension points `_initialize()`, `_newid()`, `_is_deleted()`, `empty()`, `_commit_puts_load()`, `merge_items()`, and `make_tuple_for_pickle()`.

## Control flow
Database creation uses a temporary file in the target DB directory, fast unsafe SQLite pragmas for schema setup, common incoming/outgoing sync tables and triggers, subclass initialization, commit, fsync, parent-directory lock, atomic rename, and then a normal configured connection. Existing DB connections are opened lazily by `get()`, which yields the connection, rolls back after use to close any implicit transaction, and quarantines malformed/corrupt/disk-error databases.

Writes to account/container item tables may be deferred through `put_record()`. It locks the pending file's parent directory, appends a colon-delimited base64 pickle of a subclass-defined tuple when below `PENDING_CAP`, or commits immediately when the pending file is large. `_commit_puts()` preallocates if enabled, decodes pending entries with Swift's safe unpickle helper, delegates to subclass item merging, truncates the pending file, and can include an additional immediate item. Read paths call `_commit_puts_stale_ok()` first unless commits are skipped or stale reads are allowed.

Replication helpers expose row iteration since a ROWID, sync-point get/list/merge operations, max row lookup, replication info, database ID regeneration after rsync, and timestamp merging. Metadata helpers load JSON metadata, apply timestamp-wins updates, lazily add the metadata column to older DBs, validate account/container metadata limits, clear metadata during delete, and reclaim old empty metadata. Reclaim deletes old tombstones in pages, deletes old sync rows when schema supports `updated_at`, and returns a `TombstoneReclaimer` for accounting.

## State and persistence behavior
This module is heavily persistent. It creates and mutates SQLite DB files, `.pending` files, sync tables, stat tables, metadata JSON columns, and tombstone rows. It uses atomic rename for DB creation, parent-directory locks for creation and pending commits, fsync for newly initialized DB files, optional fallocate preallocation, and quarantine renames of corrupt DB directories under `<device>/quarantined/<db_type>s/`. Pending files are append-only until committed and truncated.

## Dependencies and integration points
The broker base depends on eventlet concurrency (`sleep`, `Timeout`), SQLite, Swift constraints and UTF-8 validation, safe pickle loading, filesystem utilities (`renamer`, `mkdirs`, `lock_parent_directory`, `fallocate`, `md5`), timestamp classes, `LockTimeout`, and `HTTPBadRequest`. Account and container backend brokers subclass `DatabaseBroker` to define schema, item merge semantics, deletion rules, and pending pickle formats. Replicators, auditors, servers, and sharding code rely on its connection and replication contracts.

## Risks and edge cases
SQLite locking behavior is central: ungreened `executemany` and `executescript` are explicitly not wrapped, and code using them can block eventlet. `get()` temporarily removes `self.conn` while yielding; nested use must go through `maybe_get()` or separate broker instances. Stale reads can hide pending-file commit failures when `stale_reads_ok=True`. Pending files use pickle data, mitigated by Swift's unpickle helper but still a format requiring care. The accidental DB creation detector compares file size and ctime after `sqlite3.connect`; filesystem timestamp behavior can affect it. Metadata updates compare internal timestamp strings lexically, so callers must provide normalized timestamps. Quarantine moves whole DB directories and raises a new database error, which is correct for corruption but disruptive if false-positive strings appear in unrelated errors.

## Test signals
Tests should cover green retry behavior under locked DBs, accidental create detection, schema initialization and atomic rename, pending append/commit/truncate paths, invalid pending entries, stale read behavior, skip-commit rejection, metadata update timestamp precedence and validation, metadata column migration, delete timestamp/status updates, quarantine trigger strings, tombstone reclaim batching, sync-point merge semantics, `newid()` after rsync, reclaimable-state rules, preallocation thresholds, and subclass extension contracts.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/db.py -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/db_auditor.py -->
# sources/object-store/openstack-swift/swift/common/db_auditor.py

## Purpose
`db_auditor.py` defines `DatabaseAuditor`, the base daemon for account and container database auditors. It scans database files, opens brokers, skips deleted DBs, runs subclass-specific checks, rate-limits audit throughput, logs pass/failure counts, and writes recon cache metrics.

## Important APIs, types, and functions
- `DatabaseAuditor` inherits `Daemon`.
- `rcache` builds the recon cache file path from `recon_cache_path` and `server_type_to_recon_file(server_type)`.
- Abstract properties `server_type` and `broker_class` are implemented by account/container auditor subclasses.
- `__init__()` loads devices, mount-check mode, interval, max DBs per second, recon path, datadir, logger, rate limiter, and DB preallocation setting.
- `_one_audit_pass(reported)` iterates DB locations from `audit_location_generator()`, audits each DB, periodically logs and dumps recon counters, and rate-limits between DBs.
- `run_forever()` adds a randomized initial sleep, loops audit passes, handles exceptions/timeouts, dumps pass completion timing, and sleeps for the remaining interval.
- `run_once()` performs one pass and dumps completion timing.
- `audit(path)` creates a broker, checks deletion state, gets info, delegates to `_audit(info, broker)`, and updates pass/failure metrics.
- `_audit(info, broker)` is an abstract subclass hook.

## Control flow
An audit pass walks `<devices>/<device>/<server_type>s/**/*.db` through `audit_location_generator()` with optional mount checking. Each path is passed to `audit()`, which constructs the subclass broker, calls `is_deleted()`, then reads `get_info()` and runs subclass-specific validation. A returned exception object from `_audit()` is raised so all audit failures share the same accounting path. Every logging interval, pass/failure counters since the last report are logged and dumped to recon, then reset.

Forever mode waits a random fraction of the configured interval before the first pass to avoid synchronized cluster-wide scans. Each loop logs start/completion, catches broad exceptions and eventlet `Timeout`, increments error metrics, writes elapsed pass time to recon, and sleeps only if the pass finished faster than the configured interval.

## State and persistence behavior
The auditor is mostly read-only for database content, but opening brokers may commit pending files depending on broker behavior, and `DB_PREALLOCATION` is set globally from config. It writes recon cache JSON through `dump_recon_cache` and emits logger counters/timings. It keeps in-memory pass/failure counters that reset after each recon report.

## Dependencies and integration points
It depends on `Daemon`, eventlet `Timeout`, `audit_location_generator`, `EventletRateLimiter`, config parsing helpers, recon cache naming, and subclass broker classes. Account and container auditor daemons derive from this base to add DB-specific consistency checks.

## Risks and edge cases
Because broker `is_deleted()` and `get_info()` can touch pending commits, audits are not purely passive on DB side effects. Broad exception handling keeps the daemon alive but can mask repeated systemic failures unless recon/log metrics are monitored. Randomized initial sleep is useful operationally but must be controlled in tests. Misconfigured `max_dbs_per_second` can make passes slower than the interval, causing continuous auditing without sleep. Mount-check behavior determines whether unmounted drives are skipped or scanned as directories.

## Test signals
Tests should cover config defaults and overrides, recon path naming, rate limiter calls, logging interval counter resets, deleted DB skip behavior, subclass `_audit()` success and returned-exception failure, broker construction errors, timeout handling, forever-mode sleep calculations, run-once recon output, and `DB_PREALLOCATION` global mutation.
<!-- END_FILE_RESEARCH: sources/object-store/openstack-swift/swift/common/db_auditor.py -->
