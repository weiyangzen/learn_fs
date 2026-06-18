# subset-b-007626 research

Grouped research for the requested LizardFS source files. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/xor_read_plan.h -->
# sources/distributed-fs/lizardfs/src/common/xor_read_plan.h

Purpose: defines `XorReadPlan`, the `SliceReadPlan` specialization that post-processes reads for XOR-coded chunk slices and reconstructs one missing requested part from parity/peer data.

Important APIs/types/functions: `class XorReadPlan : public SliceReadPlan`; nested `RecoverParity` functor for building parity blocks by copying the first data part and XORing the remaining parts with `blockXor`; override `postProcessRead(uint8_t *buffer, const PartsContainer &available_parts) const`.

Control flow: `postProcessRead` first delegates to `SliceReadPlan::postProcessRead`, records available slice parts in a bitset, then finds the first requested part not present in `available_parts`. If all requested parts were read directly it returns the concatenated requested size. Otherwise it computes the missing output offset and XORs every available read operation into that missing region, copying the first available source and zero-padding short reads before applying later XORs.

State and persistence: no persistent state of its own; it relies on inherited `requested_parts`, `read_operations`, `buffer_part_size`, and debug buffer bounds. Recovery mutates only the caller-provided buffer.

Dependencies and integration: depends on `common/block_xor.h`, `common/read_plan.h`, and `common/slice_read_plan.h`; used by slice read planning for XOR goals to turn a plan that reads parity/other parts into the requested client buffer layout.

Risks: recovery assumes exactly one requested part is missing and enough compatible parts were planned; debug-only assertions guard buffer ranges but release builds depend on planner correctness. `RecoverParity` copies whole `MFSBLOCKSIZE` blocks and assumes part/block counts match the source layout.

Test signals: directly exercised by `xor_read_plan_unittest.cc`, which verifies unrecoverable configurations and successful reads from direct and parity-recovered XOR parts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/xor_read_plan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/xor_read_plan_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/xor_read_plan_unittest.cc

Purpose: GoogleTest coverage for XOR slice read planning and `XorReadPlan` recovery behavior.

Important APIs/types/functions: helper `checkUnrecoverable(ChunkPartType, PartsContainer)` expects `SliceReadPlanner::isReadingPossible()` to fail; helper `checkReadingParts(first_block, block_count, target_parts, available_parts)` builds synthetic part data, constructs a plan, executes it with `ReadPlanTester`, and compares output blocks.

Control flow: tests prepare target part indexes from `target_parts`, ask `SliceReadPlanner` to plan against available parts, build a plan for a block range, execute read operations against synthetic data, then compare each target part at the expected output offset. Four unrecoverable cases cover missing parity/incompatible slice setups; four positive cases cover direct reads and XOR recovery with nonzero block offsets.

State and persistence: test-only local maps and buffers; no persistent state.

Dependencies and integration: depends on `common/slice_read_planner.h`, `unittests/chunk_type_constants.h`, and `unittests/plan_tester.h`; validates the common read-planning layer used by client/chunk read paths.

Risks: duplicate `Unrecoverable1`/`Unrecoverable2` inputs reduce negative-case diversity. The tests validate generated output but not all malformed planner states or release-build behavior without assertions.

Test signals: this file is itself the direct test signal for XOR read plans and should run in the common unit test suite when tests are enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/xor_read_plan_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/data/CMakeLists.txt -->
# sources/distributed-fs/lizardfs/src/data/CMakeLists.txt

Purpose: installs sample data/configuration files and optionally builds the C client example.

Important APIs/functions: `configure_file` generates configured sample configs from `.in` templates; `install(FILES ...)` places metadata, master/chunkserver/client/metalogger/uRaft examples, and shell completion; test-enabled block creates mock installed headers and `c-client-example`.

Control flow: configure-time substitutions produce `mfsmaster.cfg`, `mfschunkserver.cfg`, `mfsmetalogger.cfg`, and `postinst`; install rules map each example to its component subdirectory. Under `BUILD_TESTS`, symlinked headers preserve example include paths, the C example is compiled, linked with `lizardfs-client stdc++ m`, and installed as a binary.

State and persistence: no runtime state; produces build-tree configured files and install-tree examples.

Dependencies and integration: uses CMake variables such as `DATA_SUBDIR`, `MFSMASTER_EXAMPLES_SUBDIR`, `DEFAULT_USER`, `DATA_PATH`, and library target `lizardfs-client`; passes `POSTINST_SCRIPT` to the parent scope.

Risks: example build depends on symlink support and on client headers staying at the referenced source paths. Install destinations are driven by packaging variables, so misconfigured paths affect package layout.

Test signals: `BUILD_TESTS` compiles `liblizardfs-client-example.c`, providing a syntax/link check for the public C client API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/data/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/data/globaliolimits.cfg -->
# sources/distributed-fs/lizardfs/src/data/globaliolimits.cfg

Purpose: sample global I/O limiting configuration for master-controlled bandwidth groups.

Important syntax: commented `subsystem blkio` and `limit <group> <value>` examples, including `unclassified` and nested group paths like `/some_group/some_subgroup`.

Control flow: parsed at runtime by the global I/O limits subsystem when configured through `GLOBALIOLIMITS_FILENAME`; this file itself is an example with all directives commented.

State and persistence: persisted administrator configuration; no active limits until copied/edited and comments removed.

Dependencies and integration: installed as a master example by `src/data/CMakeLists.txt`; referenced by `mfsmaster.cfg.in`.

Risks: units and subsystem behavior are not explained in this file beyond the manpage reference, so operators must consult `globaliolimits.cfg(5)`.

Test signals: no direct tests; parser coverage would be in the I/O limits code, not this sample.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/data/globaliolimits.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/data/iolimits.cfg -->
# sources/distributed-fs/lizardfs/src/data/iolimits.cfg

Purpose: sample local client/mount I/O limiting configuration.

Important syntax: commented `subsystem blkio` and `limit` examples for `unclassified` and hierarchical groups.

Control flow: consumed by client-side I/O limiting when configured; the shipped sample is entirely commented and therefore inert.

State and persistence: persisted local config template; no runtime state in the file itself.

Dependencies and integration: installed as a client example by `src/data/CMakeLists.txt`; points users to `iolimits.cfg(5)`.

Risks: same syntax as global limits can be confused with the master global limits file; operational semantics depend on the parser and cgroup/blkio support.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/data/iolimits.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/data/liblizardfs-client-example.c -->
# sources/distributed-fs/lizardfs/src/data/liblizardfs-client-example.c

Purpose: executable example for the public LizardFS C client API, demonstrating connection setup, file operations, chunkserver listing, ACLs, and POSIX-style locks.

Important APIs/functions: uses `liz_create_context`, `liz_set_default_init_params`, `liz_init_with_params`, `liz_mknod`, `liz_lookup`, `liz_open`, `liz_write`, `liz_read`, `liz_get_chunkservers_info`, ACL helpers (`liz_create_acl`, `liz_add_acl_entry`, `liz_setacl`, `liz_getacl`, `liz_print_acl`), lock helpers (`liz_setlk`, `liz_getlk`), and cleanup APIs. `register_interrupt` copies lock interrupt data into caller storage.

Control flow: connects to `localhost` using a port from argv or `9421`, recreates `testfile`, opens it, writes and reads sample bytes, prints chunkserver information, creates and round-trips an ACL, exercises lock set/query/unlock cases, then registers an interrupt callback for a conflicting lock scenario. Error paths jump to cleanup labels and return `liz_error_conv(liz_err)`.

State and persistence: creates and modifies `/testfile` under the LizardFS root, sets ACLs and locks on it, and prints status; context, connection, fileinfo, ACLs, and chunkserver info are explicitly destroyed/released.

Dependencies and integration: includes installed public headers `lizardfs/lizardfs_c_api.h` and `lizardfs/lizardfs_error_codes.h`; built by `src/data/CMakeLists.txt` under `BUILD_TESTS`.

Risks: hard-coded password `test123`, root inode, filename, and localhost master make it an example rather than a generic test. Some cleanup paths skip destroying an ACL allocated immediately before errors, so it is not a leak-free template for production code.

Test signals: compilation/linking under `BUILD_TESTS` checks API availability; runtime requires a live LizardFS master.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/data/liblizardfs-client-example.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/data/lizardfs-uraft.cfg -->
# sources/distributed-fs/lizardfs/src/data/lizardfs-uraft.cfg

Purpose: sample configuration for the LizardFS uRaft high-availability daemon.

Important settings: `URAFT_PORT`, `URAFT_STATUS_PORT`, repeated `URAFT_NODE_ADDRESS`, `URAFT_ID`, local master address/port, election timeout bounds, heartbeat period, local master health-check period, and floating IP/netmask/interface settings.

Control flow: the uRaft daemon reads these values to identify cluster peers, elect a leader, monitor the local master, and manage a floating service IP; all sample values are commented.

State and persistence: administrator-edited persistent HA configuration; no state is active in the sample.

Dependencies and integration: installed into the uRaft examples directory by the data CMake file; coordinates with local master `MATOCL` endpoint and network interface configuration.

Risks: incorrect node order/ID, timeouts, or floating IP settings can break failover or create network conflicts. The file documents defaults but does not validate topology.

Test signals: no direct tests in this subset; behavior depends on uRaft daemon config parsing and HA integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/data/lizardfs-uraft.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/data/mfschunkserver.cfg.in -->
# sources/distributed-fs/lizardfs/src/data/mfschunkserver.cfg.in

Purpose: configured sample chunkserver daemon configuration.

Important settings: daemon identity/user/group, memory lock/nice level, data path, master connection (`MASTER_HOST`, `MASTER_PORT`, timeouts), client listen host/port, worker/thread counts, read-ahead/read-behind, HDD config path, disk reserve threshold, chunk testing, no-cache and hole-punch options, load factor reporting, replication bandwidth/timeouts, chunk format and fsync policy.

Control flow: CMake substitutes install defaults like `@DEFAULT_USER@`, `@DATA_PATH@`, and `@ETC_PATH@`; the chunkserver config parser reads active uncommented settings at daemon startup/reload.

State and persistence: persistent local daemon config; controls data path and runtime behavior but stores no chunk data itself.

Dependencies and integration: installed as a chunkserver example; references `mfshdd.cfg`, master ports, chunkserver networking, disk I/O workers, and replication protocols.

Risks: duplicated settings such as `NR_OF_NETWORK_WORKERS` and `REPLICATION_BANDWIDTH_LIMIT_KBPS` appear in the sample comments with different example/default contexts, which can confuse edits. Disk, fsync, and worker settings have direct durability/performance impact.

Test signals: no direct tests; configuration names line up with chunkserver runtime modules and packaging generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/data/mfschunkserver.cfg.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/data/mfsexports.cfg -->
# sources/distributed-fs/lizardfs/src/data/mfsexports.cfg

Purpose: sample master export/access-control file for `mfsmount` clients.

Important syntax: lines are `[ip range] [path] [options]`; path `/...` exports filesystem paths and `.` exports meta; options include read-only/read-write, `alldirs`, dynamic IP, group/permission behavior, `maproot`, `mapall`, cleartext/MD5 password, minimum client version, goal bounds, and trash-time bounds.

Control flow: parsed by `master/exports.cc`; matching entries authorize client sessions based on IP, version, meta flag, path, optional challenge/response password, and privilege mapping. The shipped active lines allow read-write access to `/` with `alldirs,maproot=0` and read-write meta access for all clients.

State and persistence: persistent security policy read by the master; reloadable through the daemon reload path.

Dependencies and integration: installed as a master example and referenced by `EXPORTS_FILENAME` in `mfsmaster.cfg.in`; drives `exports_check` session outputs.

Risks: the example is permissive if copied as-is, granting broad read-write and meta access from any IP. Password examples are documentation only; cleartext passwords are hashed by the parser but still visible in config.

Test signals: no direct parser test in this subset; `exports.cc` contains the implementation used by runtime auth.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/data/mfsexports.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/data/mfsgoals.cfg -->
# sources/distributed-fs/lizardfs/src/data/mfsgoals.cfg

Purpose: sample goal definition file for replication and erasure-code placement goals.

Important syntax: `<goal id> <name-or-count> : <labels>` for standard copies, plus examples of special goals such as `$xorN` and `$ec(k,m)` with optional label constraints.

Control flow: master goal loader reads active goals to map file goal IDs to desired chunk-part layouts and media-label placement. Default goals 1-5 are active in this example; unspecified goals fall back to `min(goal_id, 5)` standard copies.

State and persistence: persistent cluster placement policy; affects chunk replication/rebalancing and file goal semantics after reload.

Dependencies and integration: installed as a master example and referenced by `CUSTOM_GOALS_FILENAME`; consumed by chunk placement, `ChunkGoalCounters`, `GoalCache`, and `ChunkCopiesCalculator`.

Risks: changing goal IDs or labels changes placement behavior for files using those goals. Examples show duplicate IDs in comments, which are illustrative but could be copied incorrectly.

Test signals: goal/counter behavior is indirectly covered by `chunk_goal_counters_unittest.cc` and broader goal loader tests outside this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/data/mfsgoals.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/data/mfshdd.cfg -->
# sources/distributed-fs/lizardfs/src/data/mfshdd.cfg

Purpose: sample chunkserver disk mount-point list.

Important syntax: one storage path per line; prefixing a path with `*` marks that mount point for removal.

Control flow: chunkserver reads the configured HDD file to discover storage directories and removal intent. The shipped file contains only commented examples.

State and persistence: administrator-managed persistent disk list; actual chunk state lives under the referenced mount points.

Dependencies and integration: installed as a chunkserver example and referenced by `HDD_CONF_FILENAME` in `mfschunkserver.cfg.in`.

Risks: mistaken active paths or removal markers can affect chunk availability and deletion/migration behavior.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/data/mfshdd.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/data/mfsmaster.cfg.in -->
# sources/distributed-fs/lizardfs/src/data/mfsmaster.cfg.in

Purpose: configured sample master/shadow metadata-server configuration.

Important settings: master personality, admin password, user/group, exports/topology/goals paths, data path, metadata recovery/backlog retention, chunk operation delay/limits, listen hosts/ports for metaloggers/chunkservers/clients/tapeservers, chunk loop pacing/CPU budget, deletion/replication limits, endangered chunk priority, balancing thresholds, inode/session options, global I/O limits, shadow-master connection, metadata checksum behavior, Berkeley DB name storage, same-IP avoidance, load factor penalty, redundancy level, snapshot batch sizing, and file-test loop timing.

Control flow: CMake fills default paths; `main.cc` loads the config at daemon startup and module reload callbacks consume individual keys. `chunks.cc` specifically reads chunk loop, deletion, replication, endangered, balancing, same-IP, and redundancy settings.

State and persistence: persistent master configuration controlling metadata storage and cluster behavior; does not itself contain metadata.

Dependencies and integration: references `mfsexports.cfg`, `mfstopology.cfg`, `mfsgoals.cfg`, `globaliolimits.cfg`, `mfsmetarestore`, shadow/master ports, and chunk maintenance modules.

Risks: settings directly affect safety and availability. `AUTO_RECOVERY`, checksum verification, deletion/replication limits, and redundancy controls are especially sensitive. Several deprecated names remain for compatibility.

Test signals: no direct tests for the sample; runtime parsers enforce some min/max constraints in modules such as `chunks.cc` and `changelog.cc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/data/mfsmaster.cfg.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/data/mfsmetalogger.cfg.in -->
# sources/distributed-fs/lizardfs/src/data/mfsmetalogger.cfg.in

Purpose: configured sample metalogger daemon configuration.

Important settings: working user/group, syslog identity, memory lock/nice level, metadata data path, changelog backlog retention, previous metadata retention, metadata download frequency, master reconnection delay, master host/port, and connection timeout.

Control flow: CMake substitutes defaults; metalogger reads active settings to connect to the master and persist metadata/changelog backups.

State and persistence: persistent daemon config; controls where replicated metadata files are stored and how often snapshots are downloaded.

Dependencies and integration: installed as a metalogger example; coordinates with master `MATOML` port and changelog retention.

Risks: too few backlogs or infrequent metadata downloads can reduce recovery coverage; incorrect master host/port leaves the metalogger stale.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/data/mfsmetalogger.cfg.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/data/mfsmount.cfg -->
# sources/distributed-fs/lizardfs/src/data/mfsmount.cfg

Purpose: sample optional default options file for `mfsmount`.

Important syntax: options can be comma-separated on one line or split across lines; examples include `mfsmaster`, `mfsport`, `mfspassword`, and an absolute default mount point.

Control flow: client mount tooling reads the file to provide default mount parameters if present; all sample lines are commented.

State and persistence: persistent local client defaults; no runtime state.

Dependencies and integration: installed as a client example by the data CMake file.

Risks: storing passwords in the config may expose credentials through local file permissions. A default mount point must be absolute.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/data/mfsmount.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/data/mfstopology.cfg -->
# sources/distributed-fs/lizardfs/src/data/mfstopology.cfg

Purpose: sample topology grouping file for master distance decisions.

Important syntax: maps IP ranges/networks/single addresses to rack/group IDs. Supports CIDR bit counts, explicit ranges, dotted netmasks, and individual addresses.

Control flow: master topology parser reads entries and assigns connecting chunkservers/mounts to groups; unspecified hosts default to group 0. Distance values feed client read-location sorting and placement/rebalancing decisions.

State and persistence: persistent topology policy; no active entries in the shipped sample.

Dependencies and integration: installed as a master example and referenced by `TOPOLOGY_FILENAME`; consumed by `topology_distance`, including calls from `chunks.cc`.

Risks: stale or overly broad ranges can bias reads/replication incorrectly. Overlapping definitions add information rather than replacing it, per the comments.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/data/mfstopology.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/data/postinst.in -->
# sources/distributed-fs/lizardfs/src/data/postinst.in

Purpose: package post-install script template for creating the default service user and data directory.

Important logic: on `configure`, checks whether `@DEFAULT_USER@` exists and creates a system user/group without a home if missing; ensures `@DATA_PATH@` exists; recursively chowns it to `@DEFAULT_USER@:@DEFAULT_GROUP@`. Other maintainer-script actions are no-ops; unknown arguments fail.

Control flow: generated by CMake with substituted defaults, then invoked by packaging with an action argument.

State and persistence: mutates host user/group database and filesystem ownership under the data path.

Dependencies and integration: uses Debian-style `adduser`, `getent`, `mkdir`, and `chown`; `POSTINST_SCRIPT` is exposed by `src/data/CMakeLists.txt`.

Risks: recursive chown of the configured data path can be expensive or dangerous if `@DATA_PATH@` is wrong. Script assumes `adduser` semantics.

Test signals: no direct tests; package install testing would validate substitutions and idempotence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/data/postinst.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/devtools/CMakeLists.txt -->
# sources/distributed-fs/lizardfs/src/devtools/CMakeLists.txt

Purpose: builds the `devtools` support library and includes the CRC utility subdirectory.

Important APIs/functions: `aux_source_directory(${CMAKE_CURRENT_SOURCE_DIR} DEVTOOLS_SOURCES)`, `add_library(devtools ${DEVTOOLS_SOURCES})`, `add_subdirectory(mycrc32)`.

Control flow: all source files directly in `src/devtools` are collected into a library; `mycrc32` is built separately as an executable.

State and persistence: build configuration only.

Dependencies and integration: library contains headers/sources such as request logging and trace helpers when enabled by compile definitions.

Risks: `aux_source_directory` can silently pick up new files and is less explicit than target source lists.

Test signals: build success is the primary signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/devtools/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/devtools/Empty.cc -->
# sources/distributed-fs/lizardfs/src/devtools/Empty.cc

Purpose: placeholder C++ translation unit for the `devtools` library.

Important APIs/functions: contains only the platform include and license header; exports no symbols.

Control flow: none.

State and persistence: none.

Dependencies and integration: included by `aux_source_directory` so the `devtools` library has at least one source even when most functionality is header-only or compile-flag-gated.

Risks: no behavioral risk; its presence can hide that a library is effectively header-only.

Test signals: compile-only.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/devtools/Empty.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/devtools/TracePrinter.h -->
# sources/distributed-fs/lizardfs/src/devtools/TracePrinter.h

Purpose: optional compile-time tracing helpers for function entry/exit and ad-hoc value logging.

Important APIs/types/functions: under `ENABLE_TRACES`, `ThreadPrinter` assigns per-thread ANSI colors and indentation, `TracePrinter` logs entry in its constructor and elapsed microseconds in its destructor, and macros `TRACETHIS`, `TRACETHIS1` through `TRACETHIS6`, `PRINTTHIS`, `PRINTTHISMSG`, and `MARKTHIS` create trace calls. Without `ENABLE_TRACES`, macros compile to `(void)0`.

Control flow: trace macros instantiate RAII objects in function scope; constructor prints `==>`, destructor prints `<==` with elapsed time. `ThreadPrinter` serializes color/indent map access with a static mutex, but printing itself happens after unlocking.

State and persistence: process-global static maps store indentation and color per `pthread_t`; output goes to stdout and is not persisted by this code.

Dependencies and integration: depends on pthreads, `gettimeofday`, `boost::format`, and `common/platform.h`; used only in builds enabling traces.

Risks: static maps grow with distinct thread IDs and are not pruned. ANSI output and stdout logging are unsuitable for normal daemon logs. Thread ID formatting with `%lx` assumes compatible `pthread_t` representation.

Test signals: no direct tests; compile coverage depends on `ENABLE_TRACES` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/devtools/TracePrinter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/devtools/configuration.h -->
# sources/distributed-fs/lizardfs/src/devtools/configuration.h

Purpose: small environment-variable configuration helper for devtool instrumentation.

Important APIs/functions: protected static `getIntWithUnitOr`, `getIntOr`, `parseIntWithUnit`, `parseInt`, and `getOptionValue`; private `doGetIntFromOption` centralizes parse-and-exit behavior.

Control flow: callers ask for an option with a default; if absent, default is returned. Integer parsing uses string streams; unit parsing accepts B/K/M/G/T suffixes as powers of 1024. Parse failures print a diagnostic to stderr and terminate with `exit(1)`.

State and persistence: stateless; reads process environment.

Dependencies and integration: used by `request_log.h` through `RequestLogConfiguration`; includes signal/stdlib/iostream/string utilities.

Risks: `parseIntWithUnit` reads `text[text.size() - 1]`, so empty strings passed directly would be invalid; public wrappers avoid empty env values by returning defaults. Multiplication may overflow `long` for large values. Exiting inside a helper is abrupt for library use.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/devtools/configuration.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/devtools/mycrc32/CMakeLists.txt -->
# sources/distributed-fs/lizardfs/src/devtools/mycrc32/CMakeLists.txt

Purpose: build definition for the `mycrc32` command-line utility.

Important APIs/functions: collects local sources into `MYCRC32_SOURCES`, creates executable `mycrc32`, and links it with `mfscommon`.

Control flow: CMake build-only; no install rule in this file.

State and persistence: build target definition only.

Dependencies and integration: utility depends on common CRC implementation from `mfscommon`.

Risks: `aux_source_directory` can include unintended future files.

Test signals: build/link success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/devtools/mycrc32/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/devtools/mycrc32/mycrc32.cc -->
# sources/distributed-fs/lizardfs/src/devtools/mycrc32/mycrc32.cc

Purpose: command-line utility that reads stdin and prints the LizardFS CRC32 of the input.

Important APIs/functions: `main()` allocates a 128 MiB plus one byte buffer, reads stdin with `fread`, rejects inputs filling the buffer, initializes CRC with `mycrc32_init`, computes `mycrc32(0, buffer, bytesRead)`, and prints hex.

Control flow: single pass read into memory, size check, null terminator write after bytes read, CRC calculation, output.

State and persistence: no persistent state; process-local heap buffer and stdout/stderr output.

Dependencies and integration: includes `devtools/mycrc32/mycrc32.h`, `common/crc.h`, Boost scoped array, and `mfscommon`.

Risks: fixed maximum input and full-buffer read make it unsuitable for streaming large files. `fread` byte count is stored in `uint32_t`, safe for the chosen limit but not a general pattern.

Test signals: no direct tests; can be manually compared against known CRC outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/devtools/mycrc32/mycrc32.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/devtools/request_log.h -->
# sources/distributed-fs/lizardfs/src/devtools/request_log.h

Purpose: optional request latency logging and average aggregation instrumentation.

Important APIs/types/functions: under `ENABLE_REQUEST_LOG`, `RequestLogConfiguration` reads env options, `DummyRTTimer` tracks microsecond lifetimes, `Compressor` wraps gzip/bzip2/none output, `TuplePrinter` writes tab-separated tuples, singleton `RequestsLog` buffers slow requests and average stats, `FunctionCallLog` and `FunctionCallAvgLog` are RAII helpers, and macros log requests or averages until scope end. Without the flag, macros are no-ops and `DummyRTTimer` is empty.

Control flow: `RequestsLog::instance()` starts a background flushing thread. Calls below `REQUEST_THRESHOLD_MS` are ignored. Request and average data are swapped under mutexes into local collections by `Flusher`, then written periodically to `REQUESTS_LOG` and `REQUESTS_LOG.avg`.

State and persistence: process-global singleton keeps bounded request vector capacity and average map; background thread writes compressed or plain log files and joins on destruction.

Dependencies and integration: depends on Boost.Iostreams gzip/bzip2, threading, mutexes, atomics, `slogger`, `massert`, and `devtools/configuration.h`. Intended for instrumentation builds, not default runtime.

Risks: default `REQUESTS_TO_BE_LOGGED` reserves up to 40 million entries, explicitly warning about multi-GB RAM use. Logging thread starts during singleton initialization and writes to stdout/stderr. Destructor join can block up to the flush sleep interval. Compression algorithm errors call `mabort`.

Test signals: no direct tests; compile coverage requires `ENABLE_REQUEST_LOG` and Boost compression support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/devtools/request_log.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/main/main.cc -->
# sources/distributed-fs/lizardfs/src/main/main.cc

Purpose: generic daemon entrypoint and lifecycle framework used by LizardFS services such as `mfsmaster`.

Important APIs/types/functions: `RunMode` command states; `initialize`, `initialize_early`, `initialize_late` run module tables; `set_syslog_ident`, `main_configure_debug_log`, `main_reload`; signal pipe handlers; `changeugid`; PAM session helpers; `FileLock` for process coordination; `makedaemon`; `createpath`; `makePidFile`; `main`.

Control flow: `main` parses flags and start/stop/restart/reload/test/kill/isalive commands, optionally daemonizes, loads config, configures logging, adjusts resource limits/PAM/nice/memory lock, drops privileges, changes to `DATA_PATH`, initializes module tables, handles lock-file semantics, then runs the event loop. Signal handlers write small control bytes to a pipe so the event loop can request exit/reload or gentle kill safely.

State and persistence: creates/removes `.APPNAME.lock` in the data directory, can write a pid file, changes process uid/gid, umask, syslog identity, resource limits, and working directory. It registers event-loop reload/destruct callbacks and closes PAM/session resources at exit.

Dependencies and integration: depends on config, event loop, logging, CRC initialization, module init tables from `init.h`, platform/PAM/systemd support, and `APPNAME`/path macros from build configuration.

Risks: lock handling mixes process control with locking and sends signals to owners. Daemonization closes inherited descriptors and uses a pipe to report startup failure. Recursive module initialization failures propagate only as status/logs. Some legacy comments and broad globals make behavior sensitive to compile-time macros.

Test signals: no direct unit tests in this subset; behavior is exercised by daemon startup/integration tests and service scripts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/main/main.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/CMakeLists.txt -->
# sources/distributed-fs/lizardfs/src/master/CMakeLists.txt

Purpose: build configuration for the master library, unit tests, and `mfsmaster` executable.

Important APIs/functions: sets include directory and definitions, `collect_sources(MASTER)`, conditionally removes Berkeley DB name storage when DB is unavailable, builds `master`, links optional Judy/DB libraries, creates/links unit tests, builds `mfsmaster` from `${MAIN_SRC}`, and configures/installs `mfsrestoremaster`.

Control flow: CMake configures target sources based on detected dependencies, then sets install rules for the daemon and helper script.

State and persistence: build/install configuration only.

Dependencies and integration: links `master` with `mfscommon` and `ADDITIONAL_LIBS`; links `mfsmaster` with PAM and optional systemd libraries; uses `APPNAME=mfsmaster` and example subdir definitions consumed by `main.cc`.

Risks: `collect_sources` and conditional source removal require dependency detection to stay in sync with actual code. Missing DB support changes available name-storage behavior.

Test signals: `create_unittest(master ${MASTER_TESTS})` and `link_unittest(master master mfscommon)` wire master tests into the build.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/acl_storage.cc -->
# sources/distributed-fs/lizardfs/src/master/acl_storage.cc

Purpose: implementation of deduplicated RichACL storage keyed by inode.

Important APIs/functions: destructor debug sanity check, `AclStorage::Hash::operator()`, `get`, `set`, `erase`, `setMode`, private `ref` and `unref`.

Control flow: `set` interns an ACL in `storage_` and maps the inode to a reference-wrapped storage entry, unrefing a previous entry if present. `erase` removes an inode mapping and decrements/removes the interned ACL. `setMode` copies the inode ACL, mutates mode bits, and re-interns only if changed. Hashing combines ACL masks, flags, and ACE fields.

State and persistence: in-memory only; `storage_` holds unique ACLs with refcounts and `acl_` maps inode IDs to interned entries.

Dependencies and integration: depends on `RichACL`, `hashCombine`, and master metadata code that stores inode ACLs.

Risks: reference wrappers into an unordered map are safe only while entries are not erased; all lifecycle changes must go through `ref`/`unref`. Destructor assertions are debug-only and not runtime recovery.

Test signals: covered by `acl_storage_unittest.cc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/acl_storage.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/acl_storage.h -->
# sources/distributed-fs/lizardfs/src/master/acl_storage.h

Purpose: declares `AclStorage`, an inode-to-RichACL map with content deduplication.

Important APIs/types/functions: `InodeId`, public noncopyable/nonmovable lifecycle, `get`, `set`, `erase`, `setMode`; private `Hash`, `AclToRefCountMap`, `KeyValue`, `InodeToKVMap`, `ref`, and `unref`.

Control flow: callers manipulate ACLs by inode; implementation interns identical `RichACL` values and tracks references rather than storing duplicates.

State and persistence: owns in-memory `storage_` and `acl_`; persistence is handled by higher-level metadata serialization, not this class.

Dependencies and integration: includes `common/richacl.h`; used by master filesystem metadata.

Risks: intentionally disables copy/move to avoid invalidating reference-wrapper invariants. Public `get` returns a pointer into internal storage that becomes invalid after mutations removing the referenced ACL.

Test signals: `acl_storage_unittest.cc` validates interning, erase, and mode update behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/acl_storage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/acl_storage_unittest.cc -->
# sources/distributed-fs/lizardfs/src/master/acl_storage_unittest.cc

Purpose: unit test for `AclStorage` deduplication and mutation behavior.

Important APIs/functions: `TEST(AclStorageTests, Basic)` creates a `RichACL`, stores it under multiple inode IDs, compares returned pointers/values, erases one mapping, and updates mode on present/absent inodes.

Control flow: verifies identical ACLs share a single interned pointer, erasing one inode does not remove another inode's ACL, `setMode` on absent inode is a no-op, and `setMode` on a present inode re-interns a changed ACL without mutating the old interned object.

State and persistence: test-local in-memory state only.

Dependencies and integration: uses GoogleTest, `master/acl_storage.h`, and `RichACL::setMode`.

Risks: tests only basic interning; does not exercise high refcounts, hash collisions, or serialization integration.

Test signals: direct coverage for ACL storage core semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/acl_storage_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/changelog.cc -->
# sources/distributed-fs/lizardfs/src/master/changelog.cc

Purpose: master/metalogger changelog writer and rotation manager.

Important APIs/functions: `changelog_init`, `changelog_get_back_logs_config_value`, `changelog_rotate`, `changelog`, `changelog_flush`, `changelog_disable_flush`, `changelog_enable_flush`, and reload callback `changelog_reload`.

Control flow: initialization stores filename and allowed `BACK_LOGS` bounds, validates config, and registers reload. `changelog` lazily opens the file in append mode, writes `<version>: <entry>`, and flushes unless disabled. Rotation closes the file and either rotates backlogs or unlinks the active file when retention is zero.

State and persistence: global filename, min/max, current backlog count, `FILE *fd`, and flush flag; persists metadata changes to changelog files.

Dependencies and integration: uses config, event-loop reload, `rotateFiles`, logging, and metadata modules that call `changelog`.

Risks: if opening fails, metadata changes are only logged as lost to syslog. Flush disabling improves performance but increases loss risk until re-enabled. Bound validation happens at init; reload uses min/max getter.

Test signals: no direct tests in this subset; behavior is critical to metadata recovery integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/changelog.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/changelog.h -->
# sources/distributed-fs/lizardfs/src/master/changelog.h

Purpose: public interface for changelog initialization, writing, rotation, and flush policy.

Important APIs/types/functions: `kMaxLogLineSize`, `changelog_init`, `changelog_get_back_logs_config_value`, `changelog_rotate`, `changelog`, `changelog_flush`, `changelog_disable_flush`, `changelog_enable_flush`.

Control flow: callers initialize with a base filename and accepted `BACK_LOGS` range, then append formatted metadata operation strings by version.

State and persistence: API controls persistent changelog files through the implementation.

Dependencies and integration: included by master metadata mutation and restoration paths.

Risks: header documents entry format but does not enforce max line length at the interface.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/changelog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/chartsdata.cc -->
# sources/distributed-fs/lizardfs/src/master/chartsdata.cc

Purpose: collects periodic master statistics into the chart subsystem.

Important APIs/functions: `chartsdata_memusage`, `chartsdata_refresh`, `chartsdata_store`, `chartsdata_term`, `chartsdata_init`; chart definitions for CPU, chunk operations, filesystem operation counters, memory, packets, and bytes.

Control flow: initialization sets CPU timers where available, samples initial memory, registers periodic refresh every 60 seconds and store every hour, and initializes `stats.mfs`. Refresh builds a `CHARTS` array initialized to no-data, samples user/system CPU via interval timers, samples memory via `getrusage` and Linux `/proc/self/statm` fallback, pulls chunk delete/replication counts, filesystem operation stats, and client network stats, then calls `charts_add`.

State and persistence: static memory usage and chart subsystem state; persists chart data through `charts_store` to `stats.mfs`.

Dependencies and integration: depends on `common/charts.h`, event loop, `chunk_stats`, filesystem stats, and `matoclserv_stats`.

Risks: CPU measurement relies on resetting interval timers and has platform-specific quirks. Memory units differ by platform and are normalized in code. Chart indices must stay aligned with `FsStats::Size` and defined offsets.

Test signals: no direct tests in this subset; runtime monitoring and chart file generation are integration signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/chartsdata.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/chartsdata.h -->
# sources/distributed-fs/lizardfs/src/master/chartsdata.h

Purpose: declares the master chart-data module interface.

Important APIs/functions: `chartsdata_memusage()` returns current memory usage sample or zero when unsupported; `chartsdata_init()` initializes chart collection.

Control flow: master init calls `chartsdata_init`; other code can query memory usage.

State and persistence: state owned by implementation; chart data is persisted by `chartsdata.cc`.

Dependencies and integration: included by master modules needing memory/metrics initialization.

Risks: small interface hides platform-dependent behavior behind `chartsdata_memusage`.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/chartsdata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/checksum.h -->
# sources/distributed-fs/lizardfs/src/master/checksum.h

Purpose: shared metadata checksum mode/status enums for master modules.

Important APIs/types: `enum class ChecksumMode { kGetCurrent, kForceRecalculate }`; `enum class ChecksumRecalculationStatus { kDone, kInProgress }`.

Control flow: callers pass `ChecksumMode` to checksum functions and receive background recalculation progress states where supported.

State and persistence: none.

Dependencies and integration: used by `chunks.cc` and likely other metadata checksum modules.

Risks: no behavioral logic; changes must stay source-compatible with checksum callers.

Test signals: compile-time use by checksum implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/checksum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/chunk_goal_counters.cc -->
# sources/distributed-fs/lizardfs/src/master/chunk_goal_counters.cc

Purpose: implements compact counting of file goals referencing a chunk.

Important APIs/functions: `addFile`, `removeFile`, `changeFileGoal`, `fileCount`, `highestIdGoal`.

Control flow: `addFile` validates goal IDs, finds insertion point by sorted goal, increments an existing counter unless it is at `uint8_t` max, otherwise inserts a new counter for that goal. `removeFile` finds and decrements/removes a counter or throws. `changeFileGoal` removes then adds. Query functions sum counts or return the highest sorted goal ID.

State and persistence: in-memory compact vector of `{goal,count}` records; persisted only through higher-level chunk metadata effects.

Dependencies and integration: uses `GoalId::isValid`; consumed by `chunks.cc` to compute superposed goals and metadata checksum compatibility.

Risks: `changeFileGoal` is not transaction-safe if `addFile(newGoal)` throws after removing the old one. Multiple counters per same goal are intentional when count exceeds 255.

Test signals: covered by `chunk_goal_counters_unittest.cc`, including high-count splitting and cache integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/chunk_goal_counters.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/chunk_goal_counters.h -->
# sources/distributed-fs/lizardfs/src/master/chunk_goal_counters.h

Purpose: declares `ChunkGoalCounters`, the compact data structure for calculating the superposition of goals for shared chunks.

Important APIs/types/functions: `GoalCounter { uint8_t goal; uint8_t count; }`, `Counters = compact_vector<GoalCounter>`, iterators, `InvalidOperation`, `addFile`, `removeFile`, `changeFileGoal`, `fileCount`, `highestIdGoal`, `size`, and `clear`.

Control flow: callers update counters as files are added, removed, or change goal; iteration exposes sorted counters for goal merging/cache keys.

State and persistence: owns compact in-memory counter vector.

Dependencies and integration: depends on `common/compact_vector.h` and exception helpers; used by chunk metadata and `GoalCache`.

Risks: counter count is `uint8_t`, requiring duplicate entries for high counts; all consumers must treat repeated goals correctly.

Test signals: `chunk_goal_counters_unittest.cc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/chunk_goal_counters.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/chunk_goal_counters_unittest.cc -->
# sources/distributed-fs/lizardfs/src/master/chunk_goal_counters_unittest.cc

Purpose: unit tests for `ChunkGoalCounters` and its interaction with `GoalCache`.

Important tests: `Add`, `Remove`, `Change`, `LotsOfGoals`, and `Cache`.

Control flow: tests validate sorted insertion, highest-goal reporting, invalid goal/remove exceptions, count increments/decrements, counter splitting when per-counter count exceeds 255, full add/remove cycles, and LRU-like `GoalCache` insert/find/eviction behavior with counters as keys.

State and persistence: test-local data only.

Dependencies and integration: uses `common/goal.h`, `master/goal_cache.h`, `master/goal_config_loader.h`, GoogleTest, and STL helpers.

Risks: cache test uses default `Goal` values and focuses on key behavior, not semantic goal merging.

Test signals: direct regression coverage for goal counter arithmetic and cache key use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/chunk_goal_counters_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/chunks.cc -->
# sources/distributed-fs/lizardfs/src/master/chunks.cc

Purpose: central master chunk metadata manager: tracks chunk IDs, versions, locks, file goal references, chunkserver copies/parts, availability/replication statistics, repair/rebalance work, metadata serialization, and checksum state.

Important APIs/types/functions: internal `ChunkPart` state machine; internal `Chunk` with `ChunkGoalCounters`, part list, stats, operation state, and checksum; global `ChunksMetadata`; public APIs from `chunks.h` including file reference updates, modification/truncate, version/location lookup, chunkserver copy status callbacks, repair, load/store/unload/newfs, checksum, and initialization. `ChunkWorker` performs maintenance jobs.

Control flow: chunks are allocated in buckets and indexed by hash of chunk ID with a last-hit cache. File operations update goal counters and checksums. Client writes/truncates use `chunk_multi_modify`/`chunk_multi_truncate`, which create new chunks, duplicate shared chunks, bump versions, lock chunks, and send create/duplicate/truncate/version messages to chunkservers. Chunkserver reports add/update/invalidate part records. Operation-status callbacks clear busy flags, mark failures, trigger emergency version increases, and notify clients. `ChunkWorker` periodically scans buckets and an endangered queue to delete invalid/unused/over-goal parts, replicate missing parts, rebalance across labels/disk usage/IPs, and remove empty chunk structs.

State and persistence: owns in-memory chunk table, next chunk ID, checksum fields, chunk copy stats, endangered queue, goal cache, delayed replication state, deletion/replication counters, and worker coroutine state. `chunk_store` serializes `nextchunkid` and chunk records with ID/version/lock timeout/lock ID; `chunk_load` restores them. Runtime copy locations are rebuilt from chunkserver reports.

Dependencies and integration: depends on goals, chunk copy calculators, chunkserver DB, filesystem metadata, topology, event loop, config, random, matocs/matocl protocols, media labels, checksum helpers, and metaserver promotion callbacks. Compile-time `METARESTORE` excludes live chunkserver maintenance for restore tooling.

Risks: correctness depends on consistent transitions among `VALID`, `BUSY`, `TDVALID`, `TDBUSY`, `INVALID`, and `DEL`. Maintenance is intentionally incremental and timing-sensitive; bad config for deletion/replication limits, loop CPU, same-IP avoidance, or endangered priority affects recovery speed and data placement. `chunk_apply_modification` used for changelog replay has less live validation than live operations. Metadata serialization stores only core chunk metadata, so copy state must be reconstructed safely.

Test signals: direct tests are not in this subset; behavior is indirectly exercised by chunk goal counter tests, read/write/truncate integration tests, metadata restore tests, and chunkserver protocol tests elsewhere.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/chunks.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/chunks.h -->
# sources/distributed-fs/lizardfs/src/master/chunks.h

Purpose: public interface for the master chunk metadata subsystem.

Important APIs/functions: version and file-reference updates (`chunk_increase_version`, `chunk_set_version`, `chunk_change_file`, `chunk_delete_file`, `chunk_add_file`), locking (`chunk_unlock`, `chunk_can_unlock`), modifications (`chunk_apply_modification`, live `chunk_multi_modify`, `chunk_multi_truncate`), stats (`chunk_stats`, `chunk_store_info`, `chunk_get_missing_count`, `chunk_store_chunkcounters`, `chunk_count`, replication/availability accessors, `chunk_info`), repair/location/copy callbacks, load/store lifecycle, checksum, and background checksum update.

Control flow: master modules call these functions from filesystem operations, chunkserver protocol handlers, metadata load/store, and daemon initialization. `METARESTORE` builds expose dump but omit live chunkserver APIs.

State and persistence: declared functions manipulate state owned by `chunks.cc`; load/store functions persist chunk metadata.

Dependencies and integration: includes chunk part/address types, chunk availability state, client-master protocol types, and checksum modes; forward-declares `matocsserventry`.

Risks: broad C-style interface exposes many state transitions without type-level sequencing guarantees; callers must respect lock/version semantics and live-vs-restore compile modes.

Test signals: linked into master unit/integration tests; no direct header-only tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/chunks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/chunkserver_db.cc -->
# sources/distributed-fs/lizardfs/src/master/chunkserver_db.cc

Purpose: maintains master-side identity records for known chunkservers keyed by IP and port.

Important APIs/functions: free-list helper `get_free_element_list`, `acquireFreeIndex`, `releaseIndex`, `csdb_new_connection`, `csdb_lost_connection`, `csdb_chunkserver_list`, `csdb_remove_server`, and `csdb_find`.

Control flow: new connections either attach to a disconnected existing record or allocate a new 13-bit ID from `gIdToCSEntry` free list. Lost connections null the live pointer but keep the record. Removal is allowed only while disconnected and releases the ID. Listing returns live server data from `matocsserv_getserverdata` or a disconnected placeholder entry.

State and persistence: static unordered map from `(ip,port)` to `csdbentry` and global ID-to-entry array/free list. State is in-memory and reconstructed from chunkserver connections.

Dependencies and integration: depends on `matocsserv` for labels/server data and `ChunkserverListEntry`; chunk copy records in `chunks.cc` store `csid` values limited by `csdbentry::kMaxIdCount`.

Risks: ID 0 is reserved/free-list head; exhaustion returns failure. The unordered-map stores entries by value, and `gIdToCSEntry` points to those values, relying on unordered_map reference stability for elements.

Test signals: no direct tests in this subset; exercised by chunkserver connection integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/chunkserver_db.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/chunkserver_db.h -->
# sources/distributed-fs/lizardfs/src/master/chunkserver_db.h

Purpose: declares chunkserver database structures and lookup/connection APIs.

Important APIs/types/functions: `csdbentry` with `kMaxIdCount = 8192`, live `matocsserventry *eptr`, `csid`, and `MediaLabel`; global `gIdToCSEntry`; `csdb_new_connection`, `csdb_lost_connection`, `csdb_chunkserver_list`, `csdb_remove_server`, `csdb_find(ip,port)`, and inline `csdb_find(id)`.

Control flow: consumers register, mark disconnected, list, remove, or find chunkserver records.

State and persistence: state owned by `chunkserver_db.cc`; no on-disk persistence.

Dependencies and integration: includes media labels and protocol chunkserver list entries; used heavily by `chunks.cc` and `matocsserv`.

Risks: `csdb_find(id)` asserts bounds but can return null for free IDs; callers must handle disconnected entries where `eptr` is null.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/chunkserver_db.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/datacachemgr.cc -->
# sources/distributed-fs/lizardfs/src/master/datacachemgr.cc

Purpose: fixed-size in-memory cache-validity tracker keyed by inode and client session.

Important APIs/functions: `dcm_open`, `dcm_access`, `dcm_modify`, `dcm_init`, and `dcm_clear`; internal `datacache_entry` table with inode hash chains and LRU links.

Control flow: `dcm_open` returns whether a session's cached inode data is valid, moving existing entries to LRU tail or recycling the LRU head for a new `(inode,sessionid)` with `cacheok=0`. `dcm_access` marks an existing entry valid and moves it to the tail. `dcm_modify` invalidates/removes entries for the same inode owned by other sessions and marks the modifying session valid if present. `dcm_init` resets hash buckets and LRU chain.

State and persistence: static arrays of 500,000 entries and 250,000 hash buckets; volatile only.

Dependencies and integration: called by master client/session file operation paths to decide whether client-side cached data remains usable.

Risks: fixed memory footprint and single global table; no locking visible here, so it assumes event-loop serialization or external synchronization. Session ID is stored in 31 bits of a bitfield.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/datacachemgr.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/datacachemgr.h -->
# sources/distributed-fs/lizardfs/src/master/datacachemgr.h

Purpose: declares the data cache manager API.

Important APIs/functions: `dcm_open(inode, sessionid)`, `dcm_access(inode, sessionid)`, `dcm_modify(inode, sessionid)`, `dcm_init`, and `dcm_clear`.

Control flow: callers open/check cache validity, mark access valid, invalidate other sessions after modification, and initialize/reset the manager.

State and persistence: implementation-owned volatile cache state.

Dependencies and integration: included by master filesystem/client operation paths.

Risks: C-style API does not expose capacity or synchronization constraints.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/datacachemgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/exports.cc -->
# sources/distributed-fs/lizardfs/src/master/exports.cc

Purpose: parses `mfsexports.cfg`, stores export records, serializes them for info queries, and authorizes client sessions.

Important APIs/functions: public `exports_info_size`, `exports_info_data`, `exports_check`, `exports_init`; internal parsers `exports_parsenet`, `exports_parsegoal`, `exports_parsetime`, `exports_parseversion`, `exports_parseuidgid`, `exports_parseoptions`, `exports_parseline`; load/reload/destruct helpers.

Control flow: initialization loads `EXPORTS_FILENAME`, parsing non-comment lines into a linked list of export records. `exports_check` normalizes requested path/meta mode, scans matching records by IP/version/path/password, verifies challenge-response MD5 when needed, chooses the most privileged/specific acceptable record, and returns session flags, UID/GID mapping, goal bounds, and trash-time bounds. Reload attempts to replace records atomically enough that parse failures keep old exports.

State and persistence: in-memory linked list `exports_records` and configured filename; source of truth is the exports config file. Records include path bytes, IP range, min version, password digest, flags, goal/trash limits, and UID/GID mappings.

Dependencies and integration: depends on config, event loop reload/destruct, MD5, goal ID validation, protocol session flags, user/group lookup, and logging. Called by master client authentication/session setup.

Risks: permissive configs grant broad access. Parser is C-style and mutates line buffers; malformed but nonfatal unknown options are ignored with warnings. Password digest uses MD5 challenge-response, which is legacy-grade security. `exports_info_data` must match serialized size calculations exactly.

Test signals: no direct tests in this subset; behavior can be validated through mount authentication and config parser tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/exports.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/exports.h -->
# sources/distributed-fs/lizardfs/src/master/exports.h

Purpose: public interface for master export information and authorization.

Important APIs/functions: `exports_info_size`, `exports_info_data`, `exports_check`, and `exports_init`.

Control flow: master initializes exports at startup, serves serialized export info to admin/status clients, and calls `exports_check` during client authentication.

State and persistence: state owned by `exports.cc`; backed by `mfsexports.cfg`.

Dependencies and integration: includes integer types and exposes protocol-level status via return codes and output parameters.

Risks: many output parameters must be non-null and interpreted consistently by callers; header does not document ownership because buffers are caller-provided.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/exports.h -->
