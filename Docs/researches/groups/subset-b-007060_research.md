# subset-b-007060 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/tgc/TapeGcTests.cc -->
# sources/distributed-fs/eos/unit_tests/mgm/tgc/TapeGcTests.cc

Purpose: GoogleTest coverage for EOS MGM tape garbage collection (`eos::mgm::tgc::TapeGc` and `TestingTapeGc`). It validates construction defaults, worker-thread startup, one-file garbage collection decisions, JSON rendering, and `MaxLenExceeded` handling.

Important APIs and fixtures: `TgcTapeGcTest` is an empty `::testing::Test` fixture. Tests instantiate `DummyTapeGcMgm`, `TapeGc`, and `TestingTapeGc`; call `getStats()`, `startWorkerThread()`, `tryToGarbageCollectASingleFile()`, `fileAccessed()`, and `toJson()`; and check `DummyTapeGcMgm` call counters such as `getNbCallsToGetTapeGcSpaceConfig()`, `getNbCallsToGetFileSizeBytes()`, and `getNbCallsToEvictAsRoot()`.

Control flow: `constructor` verifies a fresh collector has zero evicts, empty LRU, empty space stats, and a query timestamp near `time(nullptr)`. `startWorkerThread` only asserts no crash. `tryToGarbageCollectASingleFile` progressively changes fake MGM space stats and tape-GC config: no config, one accessed file, sufficient availability, then low total-bytes threshold; only the final state should fetch file size and evict once. JSON tests populate three FIDs and assert MRU-to-LRU hexadecimal ordering, then force a max-length exception.

State and persistence: All state is in-memory fake MGM state plus collector LRU state. The tests intentionally set `maxConfigCacheAgeSecs = 0`, forcing every GC attempt to refresh configuration, which explains the exact config call-count assertions.

Dependencies and integration: Depends on EOS MGM tape-GC test helpers and metadata IDs (`eos::IFileMD::id_t`) plus GoogleTest. It integrates with the tape-GC abstraction through the same public/test-only hooks used by MGM code.

Risks: The worker-thread test lacks assertions or synchronization, so regressions in actual worker behavior may pass. Timestamp assertions allow only a small future skew. JSON comparison is intentionally strict but brittle if formatting changes while semantics remain acceptable.

Test signals: This file itself is the test signal for `TapeGc`. It is strongest for decision gating and serialization order, weaker for concurrency, repeated eviction, namespace-filtering, and error propagation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/tgc/TapeGcTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/utils/AttrHelperTests.cc -->
# sources/distributed-fs/eos/unit_tests/mgm/utils/AttrHelperTests.cc

Purpose: GoogleTest coverage for EOS MGM attribute helper decisions around directory owner authorization, forced atomic upload, and versioning policy.

Important APIs and data: Tests target `eos::mgm::attr::checkDirOwner`, `attr::checkAtomicUpload`, and `attr::getVersioning`. Inputs are `eos::IContainerMD::XAttrMap` maps keyed by constants such as `SYS_OWNER_AUTH`, `SYS_FORCED_ATOMIC`, `USER_FORCED_ATOMIC`, `SYS_VERSIONING`, and `USER_VERSIONING`, plus `eos::common::VirtualIdentity`.

Control flow: `checkDirOwner` coverage includes an empty xattr map, sticky-owner wildcard (`*`), and protocol/user matching (`krb5:testuser`) that should rewrite `dir_uid` and `dir_gid` to the caller identity. Atomic upload tests exercise no attributes, system attribute truthy/falsy/negative/garbage values, user attributes, CGI-triggered atomic upload, and system override precedence. Versioning tests validate CGI string parsing, invalid CGI fallback behavior, CGI override of xattrs, system override of user values, garbage system values, and user-only values.

State and persistence: No persistent state. Each test creates a local xattr map and identity. Mutations are intentionally performed in-place inside test bodies to verify precedence after key changes.

Dependencies and integration: Depends on `mgm/utils/AttrHelper.hh`, MGM constants, namespace metadata xattr map type, and GoogleTest. It is an integration-style unit test because policy constants and helper parsing are checked together.

Risks: Tests cover representative string values but not whitespace, comma edge cases beyond owner auth, very large version values, negative versioning, or null diagnostics behavior beyond passing `nullptr` to `checkDirOwner`. The `checkDirOwner` test uses `EXPECT_TRUE` followed by hard assertions, so a failed owner match still checks mutated IDs.

Test signals: Strong signal for xattr precedence and numeric conversion behavior. A regression that changes sys-over-user priority or invalid string handling should fail here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/unit_tests/mgm/utils/AttrHelperTests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/glusterfsd/Makefile.am -->
# sources/distributed-fs/glusterfs/glusterfsd/Makefile.am

Purpose: Automake directory dispatcher for the GlusterFS daemon subtree. It delegates all actual daemon build rules to `glusterfsd/src`.

Important build declarations: `SUBDIRS = src` makes the `src` directory participate in recursive Automake targets. `CLEANFILES =` is empty, so this level contributes no generated cleanup artifacts.

Control flow: During configure-generated make execution, standard recursive targets (`all`, `install`, `clean`, etc.) enter `src` in order. This file has no conditional logic.

State and persistence: No runtime state and no generated files at this level. Persistent installation behavior is defined in `src/Makefile.am`.

Dependencies and integration: Integrates with the top-level GlusterFS Automake hierarchy by exposing `glusterfsd/src` as a subdirectory. It assumes the top-level configure files define the usual recursive Automake environment.

Risks: Low technical risk. If future files are added at this directory level, they will not be built or cleaned until this file gains explicit rules.

Test signals: Build-system validation is the signal: `make`, `make install`, and `make distcheck` should traverse into `src`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/glusterfsd/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/glusterfsd/src/Makefile.am -->
# sources/distributed-fs/glusterfs/glusterfsd/src/Makefile.am

Purpose: Automake rules for building and installing the GlusterFS daemon binaries: `glusterfsd`, conditionally `gf_attach`, plus compatibility symlinks `glusterfs` and `glusterd`.

Important build declarations: `sbin_PROGRAMS` always includes `glusterfsd`; under `WITH_SERVER`, it also includes `gf_attach` and repeats `glusterfsd`. `glusterfsd_SOURCES` are `glusterfsd.c` and `glusterfsd-mgmt.c`; `gf_attach_SOURCES` is `gf_attach.c`. Both link against `libglusterfs`, RPC libraries, and XDR libraries; `gf_attach` also links `libgfapi`. `noinst_HEADERS` lists daemon-private headers. `AM_CPPFLAGS` injects config paths (`DATADIR`, `CONFDIR`, `XLATORDIR`, `LIBEXECDIR`) and include paths for libglusterfs, RPC, XDR, NFS/server, protocol/server, and API headers.

Control flow: A dependency rule forces `libglusterfs.la` to build before daemon linking. `install-data-local` creates runtime/log directories and installs symlinks: `glusterfs -> glusterfsd`, and under `WITH_SERVER`, `glusterd -> glusterfsd`. `uninstall-local` removes those symlinks.

State and persistence: Persists installed binaries, symlinks, and directories under `$(localstatedir)/run`, `$(localstatedir)/run/gluster`, and `$(localstatedir)/log/glusterfs`.

Dependencies and integration: This is the build integration point for daemon startup (`glusterfsd.c`), management RPC (`glusterfsd-mgmt.c`), and brick attach helper (`gf_attach.c`). Compile-time macros define the runtime paths consumed by the C code.

Risks: The conditional `sbin_PROGRAMS += glusterfsd gf_attach` duplicates `glusterfsd` when `WITH_SERVER` is enabled; Automake usually tolerates this but it is fragile. Symlink install/remove uses `rm -f` and `ln -s`, so package scripts must ensure correct permissions and paths.

Test signals: `make`, `make install DESTDIR=...`, and package builds with and without `WITH_SERVER` should verify program lists, link dependencies, and symlink creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/glusterfsd/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/glusterfsd/src/gf_attach.c -->
# sources/distributed-fs/glusterfs/glusterfsd/src/gf_attach.c

Purpose: Command-line helper that connects to a running glusterfsd brick-operation Unix-domain socket and sends an attach or detach request.

Important APIs and functions: Defines `gf_attach_actors` and `gf_attach_prog` for the `GD_BRICK_PROGRAM`. `my_callback()` records RPC status and wakes the main thread. `send_brick_req()` builds a `gd1_mgmt_brick_op_req`, XDR-serializes it into an iobuf, waits for RPC connection, submits `GLUSTERD_BRICK_ATTACH` or `GLUSTERD_BRICK_TERMINATE`, then waits for callback completion. `sanitize_args()` validates socket/volfile/brick-path types. `main()` parses `-d`, initializes a minimal `glfs_t`, builds RPC transport options, starts `rpc_clnt`, and calls `send_brick_req()`.

Control flow: Attach mode is `gf_attach uds_path volfile_path`; detach mode is `gf_attach -d uds_path brick_path`. The tool validates arguments before creating RPC state. It waits up to 60 seconds for connection and 120 seconds for reply. Success prints `OK`; RPC errors or timeouts return `EXIT_FAILURE`.

State and persistence: Uses global `done` and `rpc_status` guarded by a mutex/condition variable. It does not persist files; it only reads path metadata and sends one RPC.

Dependencies and integration: Depends on libgfapi initialization for a Gluster context, RPC client APIs, iobuf/iobref memory, XDR generated types from glusterd, and Unix socket transport options. It integrates with handlers in `glusterfsd-mgmt.c`.

Risks: Global completion state means the process is single-request only. Some early failure paths return without unrefing all allocated objects. The wait loops rely on condition variables and can block until timeout if notification is missed. `sanitize_args()` switches on full `argc`, so option parsing assumptions are coupled to exact CLI forms.

Test signals: Useful tests would cover invalid path type rejection, attach/detach request serialization against a fake RPC server, connection timeout, reply timeout, and server-side error propagation. No direct tests are present in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/glusterfsd/src/gf_attach.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/glusterfsd/src/glusterfsd-mem-types.h -->
# sources/distributed-fs/glusterfs/glusterfsd/src/glusterfsd-mem-types.h

Purpose: Declares daemon-specific memory accounting type IDs used with GlusterFS allocation wrappers.

Important types: `GF_MEM_TYPE_START` begins after `gf_common_mt_end`. `enum gfd_mem_types_` assigns IDs for daemon xlator list entries, xlators, server command-line structures, xlator command-line options, daemon-owned chars, call pools, and `gfd_mt_end`.

Control flow: There is no executable control flow. The enum values are consumed by allocation calls such as `GF_CALLOC(..., gfd_mt_xlator_t)` and by `xlator_mem_acct_init(THIS, gfd_mt_end)` in daemon startup.

State and persistence: No runtime state by itself. Its IDs affect memory accounting counters and diagnostics during a process lifetime.

Dependencies and integration: Depends on `<glusterfs/mem-types.h>`. Integrated by `glusterfsd.c` and any daemon source that uses daemon-specific allocation tags.

Risks: IDs must remain contiguous and after common memory types. Adding an enum after `gfd_mt_end` or failing to update callers can corrupt accounting categories. Renaming values is less risky than reordering if external reports are interpreted by name.

Test signals: Memory-accounting initialization and statedump/mempool reports should show daemon allocation classes. Compile failures catch missing enum names; runtime leak attribution depends on accounting tests or diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/glusterfsd/src/glusterfsd-mem-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/glusterfsd/src/glusterfsd-messages.h -->
# sources/distributed-fs/glusterfs/glusterfsd/src/glusterfsd-messages.h

Purpose: Central message-ID registry and message string definitions for the `GLUSTERFSD` logging component.

Important APIs and constants: Uses `GLFS_MSGID(GLUSTERFSD, ...)` to declare stable message IDs, then maps symbolic IDs like `glusterfsd_msg_1_STR` through `glusterfsd_msg_43_STR` and compatibility IDs `glusterfsd_msg_029_STR`, `glusterfsd_msg_041_STR`, and `glusterfsd_msg_042_STR` to log text.

Control flow: No runtime control flow; logging macros in daemon C files reference these symbols. The header comments define the governance rule: append new IDs, never delete IDs, and keep the component name aligned with `glfs-message-id.h`.

State and persistence: No state. The persistent contract is log/message ID stability for operators, documentation, and tooling.

Dependencies and integration: Depends on `<glusterfs/glfs-message-id.h>`. Integrated across `glusterfsd.c` and `glusterfsd-mgmt.c` via `gf_smsg`/`gf_msg` calls.

Risks: Reusing/removing IDs breaks log consumers and support tooling. Some message strings contain spelling mistakes preserved for compatibility, so cleanup edits may be externally visible. The out-of-order defines are intentional but easy to mishandle.

Test signals: Compile/link catches missing IDs. Operational log tests or message catalog checks are needed to catch accidental ID reuse or changed strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/glusterfsd/src/glusterfsd-messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/glusterfsd/src/glusterfsd-mgmt.c -->
# sources/distributed-fs/glusterfs/glusterfsd/src/glusterfsd-mgmt.c

Purpose: Management RPC implementation for glusterfsd. It handles volfile fetch/reconfiguration, brick attach/detach, translator operations, status/profile/metrics requests, portmap sign-in, listener setup, and management-client reconnect behavior.

Important APIs and functions: Public entry points are `glusterfs_mgmt_init()`, `glusterfs_listener_init()`, `glusterfs_volfile_fetch()`, `glusterfs_mgmt_notify()`, and `mgmt_submit_request()`. Key handlers include `glusterfs_handle_terminate()`, `glusterfs_handle_attach()`, `glusterfs_handle_svc_attach()`, `glusterfs_handle_svc_detach()`, `glusterfs_handle_translator_info_get()`, `glusterfs_handle_translator_op()`, `glusterfs_handle_brick_status()`, `glusterfs_handle_node_status()`, `glusterfs_handle_nfs_profile()`, `glusterfs_handle_volume_barrier_op()`, `glusterfs_handle_barrier()`, `glusterfs_handle_bitrot()`, `glusterfs_handle_defrag()`, and `glusterfs_handle_dump_metrics()`.

Control flow: Management callbacks use a consistent pattern: decode XDR request, unserialize input dictionaries, locate the active graph/xlator, issue an xlator notify or local operation, serialize a response dictionary, and free XDR-owned buffers. Volfile paths compute SHA-256 checksums, compare against `ctx->volfile_list`, and choose no-op, option reconfigure, graph reconstruct, service attach, or multiplexed reconfigure. `mgmt_rpc_notify()` reacts to disconnect/connect by rotating volfile servers, refetching specs, signing in brick ports, or terminating if startup cannot obtain a graph.

State and persistence: Mutates `glusterfsd_ctx`, `ctx->active`, `ctx->volfile_list`, volfile checksums, `ctx->listener`, `ctx->mgmt`, portmap registration state, and static flags `is_mgmt_rpc_reconnect` and `need_emancipate`. Temporary volfiles are created with `mkstemp`, unlinked immediately, and fed to graph processing. Status/metrics handlers read process state and dump data into dictionaries or response strings.

Dependencies and integration: Depends on Gluster RPC client/server layers, XDR types, dictionaries, iobufs, graph/xlator APIs, server translator internals, portmap and handshake programs, monitoring, statedump, and daemon lifecycle functions from `glusterfsd.c`. It is the server counterpart to `gf_attach.c`.

Risks: This file is concurrency-sensitive around `ctx->volfile_lock` and graph mutation. Many handlers manually manage XDR buffers and dictionaries, so cleanup-path leaks or double frees are plausible. Some operations return success for idempotent detach/not-found cases. Temporary file and graph-reconfiguration paths must preserve checksum/list consistency. Reconnect logic can terminate the process during startup if no volfile server works.

Test signals: Best coverage would combine RPC integration tests, volfile checksum/reconfigure tests, brick mux attach/detach tests, and fault injection for XDR/dict/graph failures. No direct tests are in this subset; runtime validation likely comes from Gluster daemon integration suites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/glusterfsd/src/glusterfsd-mgmt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/glusterfsd/src/glusterfsd.c -->
# sources/distributed-fs/glusterfs/glusterfsd/src/glusterfsd.c

Purpose: Main executable implementation for `glusterfsd`/`glusterfs`/`glusterd` modes. It parses command-line options, initializes global context and logging, configures FUSE mount options, daemonizes, installs signal handling, loads or fetches volume graphs, starts the I/O framework, and coordinates shutdown.

Important APIs and functions: `main()` is the process entry point. Major internal paths include `parse_opts()`, `parse_cmdline()`, `glusterfs_ctx_defaults_init()`, `logging_init()`, `create_fuse_mount()`, `daemonize()`, `glusterfs_signals_setup()`, `glusterfs_sigwaiter()`, `cleanup_and_exit()`, `volfile_init()`, `glusterfs_process_volfp()`, `glusterfs_volumes_init()`, `main_start()`, `main_terminate()`, `reincarnate()`, and `emancipate()`. Exported functions include `glusterfs_process_volfp()`, `cleanup_and_exit()`, and `emancipate()`.

Control flow: Startup checks memory-accounting flags, creates `glusterfs_ctx_t`, initializes globals/default pools, parses options, handles print-only modes, initializes logging, validates brick-mux mode, creates a FUSE xlator when a mount point is present, daemonizes, then runs `gf_io_run()` with `main_start`/`main_terminate`. `main_start()` initializes memory pools, async threading, OOM score, syncenv, timer wheel, and volumes. Volume initialization starts a local listener, connects to management for remote volfiles, or loads a local volfile. SIGHUP triggers volfile reload/refetch and graph notification; SIGTERM/SIGINT trigger cleanup.

State and persistence: Owns global `glusterfsd_ctx`. Initializes pools, event loop, client table, command-line lists, pidfile, log files, daemon pipe, signal thread, active graph, volfile checksums, and optional FUSE root xlator. Persistent effects include pidfile writes, log file/symlink handling, daemon fork status, FUSE mount setup, and OOM proc-file writes on Linux.

Dependencies and integration: Depends broadly on libglusterfs context, graph, xlator, dict, logging, event, timer, syncop, monitoring, daemon, and I/O APIs plus management functions from `glusterfsd-mgmt.c`. Compile-time macros from `Makefile.am` provide default directories.

Risks: Command-line parsing has many interacting options and precedence rules. Signal cleanup intentionally exits while holding `cleanup_lock`, which is deliberate but fragile. Daemon parent/child synchronization depends on `emancipate()`. Graph reload paths must avoid loading FUSE translators from volfiles and must maintain active graph consistency. Manual allocation and ownership of option strings, xlator options, and FILE pointers require careful cleanup.

Test signals: Needs CLI parsing tests, daemonization/pidfile tests, signal/reload integration tests, local and remote volfile graph tests, FUSE option propagation tests, and process-mode tests. In this subset, build linkage and daemon integration suites are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/glusterfsd/src/glusterfsd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/glusterfsd/src/glusterfsd.h -->
# sources/distributed-fs/glusterfs/glusterfsd/src/glusterfsd.h

Purpose: Private daemon header for default paths, CLI option keys, daemon constants, and cross-file function prototypes.

Important APIs and types: Defines default volfile paths, event-pool size, accepted log-level strings, daemon/debug flags, mempool sizing constants, and `GLUSTER_BRICK_GRACEFUL_CLEANUP`. `enum argp_option_keys` assigns stable short and numeric keys used by `argp` in `glusterfsd.c`. Prototypes expose `glusterfs_mgmt_init()`, `glusterfs_listener_init()`, `glusterfs_volfile_fetch()`, `glusterfs_process_volfp()`, `emancipate()`, and `cleanup_and_exit()`. Declares external `glusterfsd_ctx`.

Control flow: No executable flow. Its enum drives `parse_opts()` switch dispatch and therefore the entire CLI control path.

State and persistence: No direct state. Constants affect runtime defaults for config files, event-pool sizing, memory pools, and brick cleanup behavior. The `glusterfsd_ctx` declaration exposes the process-global context.

Dependencies and integration: Shared by `glusterfsd.c` and `glusterfsd-mgmt.c`. Assumes compile-time `CONFDIR` and related macros are provided by Automake flags.

Risks: Numeric argp keys must not collide. Changing default paths affects startup behavior and packaging. Changing mempool counts impacts memory footprint and allocation behavior. The global context declaration cements singleton daemon assumptions.

Test signals: Compile catches missing prototypes and duplicate enum symbols; CLI integration tests catch key/default regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/glusterfsd/src/glusterfsd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/Makefile.am -->
# sources/distributed-fs/glusterfs/libglusterfs/Makefile.am

Purpose: Automake dispatcher for the core `libglusterfs` subtree.

Important build declarations: `SUBDIRS = src` delegates all library compilation, generated sources, and header installation to `libglusterfs/src`. `CLEANFILES =` is empty at this directory level.

Control flow: Recursive Automake targets enter `src`. This file has no conditionals or local targets.

State and persistence: No runtime state and no installed files directly from this level.

Dependencies and integration: Integrates the core library source directory into the top-level GlusterFS build. All substantive dependencies are defined in `src/Makefile.am`.

Risks: Low. New files placed directly under `libglusterfs/` would be invisible to the build unless rules are added.

Test signals: Build traversal through `src` during `make`, `make clean`, and distribution targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/Makefile.am -->
# sources/distributed-fs/glusterfs/libglusterfs/src/Makefile.am

Purpose: Main Automake recipe for building `libglusterfs.la`, installing public GlusterFS headers, and generating parser/default/event headers for the core library.

Important build declarations: Builds `lib_LTLIBRARIES = libglusterfs.la` from a large source list covering dicts, xlators, logging, event loops, memory pools, graph parsing, syncops, monitoring, async threading, and I/O backends. Conditional sources include bundled `xxhash`, `libexecinfo`, `run.c` versus `run_fork.c`, events, and io_uring. Public headers install under `$(includedir)/glusterfs`; changelog header installs under a gfchangelog include dir. `nodist` sources include generated `y.tab.c`, `graph.lex.c`, and `defaults.c`.

Control flow: Build generates `eventtypes.h`, parser lexer/YACC outputs, and `defaults.c` before compiling. Link flags set libtool versioning and export symbols from `libglusterfs.sym`. Conditional sections adapt to platform/library availability and build options.

State and persistence: Produces the installed shared library and public headers. Generated files are cleaned via `CLEANFILES`; unit-test mode adds coverage and xunit cleanup patterns.

Dependencies and integration: Links zlib, math, UUID, dl, userspace-RCU, RCU CDS, resolver, and optional contrib libraries. Provides the core APIs consumed by `glusterfsd`, translators, RPC code, and helpers. Compile-time macros define xlator directories, sbindir, large-file behavior, and namespace selection for xxhash.

Risks: Source/header list drift can break installed API or omit objects from the library. Generated parser dependencies must be ordered correctly for parallel builds. Conditional bundled-library paths must match configure checks. Export-symbol mismatch can hide new APIs.

Test signals: `make -j`, `make distcheck`, install-header checks, ABI/export checks, and builds across feature combinations (`BUILD_EVENTS`, `BUILD_LINUX_IO_URING`, missing libxxhash/backtrace) are the primary validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/async.c -->
# sources/distributed-fs/glusterfs/libglusterfs/src/async.c

Purpose: Implements GlusterFS global asynchronous worker-thread pool used when `global_threading` is enabled outside glusterd. The design minimizes queue contention with userspace-RCU wait-free queues and signal-based leader/worker coordination.

Important APIs and functions: Public APIs are `gf_async_init()`, `gf_async_fini()`, and `gf_async_adjust_threads()`, with work submission supplied by macros/types in `glusterfs/async.h`. Internal functions include signal wrappers, `gf_async_worker_create()`, `gf_async_worker_enable()`, `gf_async_leader_run()`, `gf_async_worker_run()`, `gf_async_stop_check()`, `gf_async_stop_all()`, `gf_async_join()`, `gf_async_terminate()`, and `gf_async_worker()`. Global state is `gf_async_ctrl`, static worker table `gf_async_workers`, and thread-local `gf_async_current_worker`.

Control flow: Initialization resets state, skips disabled/glusterd modes, sets max threads, initializes queues and signal masks, blocks async signals, installs safety handlers, creates spare workers, and wakes the initial leader. A leader waits for queue signals, dequeues one job, enables another worker as future leader, runs the job, then drains available work as a normal worker. Shutdown sets max threads to zero, enqueues stop propagation, synchronizes with the last worker via barrier, joins it, flushes pending signals, restores handlers, and resets state.

State and persistence: State is in-process only: worker stack, work queue, atomic packed counts for running/stopping workers, signal masks/old handlers, barrier, max-thread count, and current-worker TLS. No files are persisted.

Dependencies and integration: Depends on pthreads, POSIX signals, userspace-RCU queues/stacks, Gluster atomics, thread naming, logging/error helpers, and `glusterfs_ctx_t` command/process mode. `glusterfsd.c` initializes it from `main_start()`.

Risks: Signal-mask correctness is critical; an unblocked async signal in any thread is treated as fatal. Worker scaling relies on packed atomic counters. Shutdown intentionally processes join jobs through the same async queue, so missed stop propagation can deadlock. Static worker storage avoids early allocator issues but caps maximum concurrency.

Test signals: Needs stress tests for concurrent submission, dynamic thread adjustment, shutdown with queued work, disabled mode, signal-mask violations, and max-thread limits. In this subset there are no direct tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/libglusterfs/src/async.c -->
