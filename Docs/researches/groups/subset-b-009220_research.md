# subset-b-009220 Filebench Research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/flowop.c -->
# sources/test-tools/filebench/flowop.c

Purpose: implements Filebench flowop lifecycle and scheduling. It defines prototype, master, runtime, and composite flowops; creates runtime instances for worker threads; repeatedly executes each thread's `fo_exec_next` chain; records latency/bytes/count statistics; and destroys flowop-local resources at thread exit.

Important APIs/functions: `flowop_init()` registers generic and filesystem-specific flowops and initializes plugin vectors; `flowop_start()` is the worker thread main loop; `flowop_define()` and `flowop_new_composite_define()` allocate shared-memory flowops; `flowop_find*()` resolves global and recursive flowop names; `flowop_beginop()`/`flowop_endop()` update timing, byte, read/write, global `controlstats`, and optional latency histogram state. Generic init/destruct helpers are used by `flowop_library.c` prototypes.

Control flow: master initialization loads prototype flowops. Parser-created `FLOW_MASTER` flowops are copied into runtime instances inside `flowop_start()` while holding `shm_flowop_lock` and a read side of `shm_flowop_find_lock`; find operations take the write side as a barrier so target lookups wait until runtime creation finishes. The main loop checks thread/global abort flags, quiet mode, and process readiness, then executes the current flowop `fo_iters` times and advances cyclically. Composite flowops recurse through inner flowops and propagate `FILEBENCH_OK`, `FILEBENCH_ERROR`, `FILEBENCH_NORSC`, or `FILEBENCH_DONE`.

State/persistence: all flowop objects are allocated from IPC shared memory and linked both globally (`fo_next`) and per execution list (`fo_exec_next`/`fo_comp_fops`). Per-flowop mutexes, condition variables, private buffers, semaphores, constants, timestamps, target lists, and stats live in `flowop_t`. Runtime thread memory may come from normal heap or ISM.

Dependencies/integration: depends on `filebench_shm`, IPC locks/allocators, parser-created threadflow/procflow structures, fileset lookup, stats data, eventgen counters, ioprio, and flowop library callbacks. `fb_lfs_newflowops()` and `fb_lfs_funcvecinit()` attach local filesystem behavior.

Risks: runtime instance creation inherits whole `flowop_t` objects and must carefully reinitialize locks and list pointers. `flowop_composite_destruct()` advances after deleting the current inner flowop, which is sensitive to use-after-free if deletion mutates links unexpectedly. Stats updates protect global counters but per-flowop stats are updated by owning execution without broad locking. Error paths often call `filebench_shutdown(1)`, so malformed workloads can terminate the whole run.

Test signals: run WML scripts with simple read/write loops, composite flowops, target wakeups, and no-resource modes; confirm flowop lists, instance numbers, abort behavior, latency histograms, and stats totals. Concurrency tests should cover multiple process/thread instances and target lookup ordering.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/flowop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/flowop.h -->
# sources/test-tools/filebench/flowop.h

Purpose: declares the central `flowop_t` execution object, flowop prototype descriptors, type/attribute constants, statistics globals, and lifecycle APIs used by parser, proc/thread execution, and flowop libraries.

Important APIs/types: `flowop_t` holds identity, global/execution/composite links, local variables, thread backpointer, callback function pointers, type/attrs, fileset/fd attributes, AVD runtime attributes, target linkage, stats, synchronization primitives, private buffers, semaphore state, and throughput limiter fields. `flowop_proto_t` maps built-in names to init/execute/destruct callbacks. Constants distinguish prototype (`FLOW_DEFINITION`), inner composite prototype (`FLOW_INNER_DEF`), master script instance (`FLOW_MASTER`), and runtime instances.

Control flow contract: parser code creates `FLOW_MASTER` objects from prototypes and sets AVD attributes. Worker startup clones them into runtime instances. `fo_func`, `fo_init`, and `fo_destruct` are invoked by `flowop.c`; helper APIs expose define/find/init/delete/print and I/O setup to `flowop_library.c`.

State/persistence: instances are shared-memory objects from `ipc_malloc(FILEBENCH_FLOWOP)`. Attributes are mostly `avd_t` so values can be constants, variables, random distributions, or composite locals. Buffers and `fo_private` are process-local allocations owned by callbacks and destructors.

Dependencies/integration: includes `filebench.h`, which supplies `threadflow_t`, `fileset_t`, `avd_t`, `flowstats`, `fb_fdesc_t`, and timing types. Declares local filesystem plugin initialization hooks.

Risks: the struct is copied wholesale for inheritance, so any new pointer or synchronization field needs explicit reset/reinitialization in `flowop_define_common()`. Attribute bitmasks are used for stats classification and file flags; inconsistent callback metadata can corrupt accounting.

Test signals: ABI/build checks should compile every flowop callback table entry; runtime tests should ensure cloned flowops have independent locks, buffers, target lists, and stats.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/flowop.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/flowop_library.c -->
# sources/test-tools/filebench/flowop_library.c

Purpose: implements Filebench's built-in WML flowops. It supplies the prototype table consumed by `flowoplib_flowinit()` and the execution logic for I/O, file metadata operations, synchronization, rate limiting, finish conditions, delays, printing, and random-variable validation.

Important APIs/functions: `flowoplib_funcs[]` registers names such as `read`, `write`, `openfile`, `createfile`, `closefile`, `deletefile`, `fsync`, `fsyncset`, `makedir`, `removedir`, `listdir`, `statfile`, `readwholefile`, `writewholefile`, `appendfile`, `appendfilerand`, `block`, `wakeup`, `semblock`, `sempost`, `eventlimit`, `bwlimit`, `iopslimit`, `opslimit`, `finishoncount`, `finishonbytes`, `hog`, `delay`, `print`, and `testrandvar`. Public `flowoplib_iosetup()` composes fd selection/opening, working-set discovery, and buffer allocation/alignment.

Control flow: each flowop resolves the needed fd with `flowoplib_fdnum()`, may select a `filesetentry_t` through `fileset_pick()`, performs plugin-dispatched filesystem calls through `FB_*` macros, wraps measured work in `flowop_beginop()`/`flowop_endop()`, and returns Filebench status codes. Rate limiters consume eventgen queue credits based on global or target flowop stats. Semaphore flowops use System V semaphores when available, otherwise POSIX semaphores. Finish flowops return `FILEBENCH_NORSC` when thresholds are reached.

State/persistence: thread fd arrays (`tf_fd`, `tf_fse`, `tf_fdrotor`) carry open file state between flowops. Fileset entries track existence, busy state, open counts, and idle counters. `fo_buf` is resized lazily for private buffers; `tf_mem` is used for random I/O buffer offsets. `fo_targets`, `fo_tputbucket`, and `fo_tputlast` cache target and limiter state.

Dependencies/integration: depends on `flowop.c` timing/stat helpers, `fileset` allocation/open/unbusy, random helpers, eventgen shared state, IPC locks/semaphores, filesystem plugin vector, and platform flags for direct I/O, fadvise, semtimedop, and System V semaphores.

Risks: several paths ignore return values from filesystem calls such as unlink/mkdir/rmdir/fsync, so benchmark state may diverge from storage reality. The fd and fileset invariants are strict; opening twice, closing closed fds, raw-device misuse, or conflicting fd/fileset names abort or error. Direct I/O alignment is hand-rolled. Event and semaphore flowops can block indefinitely or for long timeouts if paired targets are missing or eventgen stops unexpectedly. `flowoplib_read()` calls `flowop_endop()` twice on read error in one branch.

Test signals: WML coverage should exercise every registered flowop, fd rotation, raw device/open flags, random/sequential read/write offsets, no-resource fileset exhaustion, event rate limiting, semblock/sempost pairing, finish conditions, and teardown of `testrandvar` private state.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/flowop_library.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/fsplug.h -->
# sources/test-tools/filebench/fsplug.h

Purpose: defines Filebench's filesystem plugin abstraction. Built-in flowops call `FB_*` macros instead of direct POSIX calls so local, NFS, CIFS, or other client backends can share WML flowop semantics.

Important APIs/types: `fb_plugin_type_t` enumerates `LOCAL_FS_PLUG`, `NFS3_PLUG`, `NFS4_PLUG`, and `CIFS_PLUG`. `fb_fdesc_t` is a union of OS fd integer or backend pointer. `fsplug_func_t` contains function pointers for memory advice, open/read/write/pread/pwrite/lseek/truncate/rename/close/link/symlink/unlink/readlink/mkdir/rmdir/opendir/readdir/closedir/fsync/stat/fstat/access/recursive remove. `fs_functions_vec` is the active dispatch table.

Control flow: `flowop_init()` selects the active vector from `filebench_shm->shm_filesys_type`; `flowop_library.c` invokes `FB_OPEN`, `FB_PREAD`, `FB_WRITE`, and related macros, which indirect through `fs_functions_vec`.

State/persistence: the active vector is process-global, while descriptors are stored per threadflow in `fb_fdesc_t` slots. Backend-specific persistent state can live behind `fd_ptr`.

Dependencies/integration: includes `filebench.h` for platform types and is consumed heavily by flowop libraries and fileset operations. Local filesystem support is installed by `fb_lfs_funcvecinit()`.

Risks: macros do not check that `fs_functions_vec` or individual callbacks are non-null, so initialization order is critical. The union descriptor requires each backend to consistently set and test the correct member; code frequently checks `fd_ptr` even for local fds.

Test signals: plugin initialization tests should assert all callbacks used by built-in flowops are populated. Backend smoke tests should compare local POSIX behavior with macro-dispatched behavior for all file and directory operations.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/fsplug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/gamma_dist.c -->
# sources/test-tools/filebench/gamma_dist.c

Purpose: samples gamma-distributed random values for Filebench random variables using algorithms from Knuth. It supports the default `drand48()` source or an injected uniform random source plus caller-supplied seed state.

Important APIs/functions: `gamma_dist_knuth(a, b)` uses `drand48()` and returns `b * sample`. `gamma_dist_knuth_src(a, b, src, xi)` does the same with a provided `double (*src)(unsigned short *)`. Internal `gamma_dist_knuth_algG()` handles `0 < a <= 1`; `gamma_dist_knuth_algA()` handles `a > 1`.

Control flow: the public functions branch on `a <= 1.0`. Algorithm G uses rejection sampling with an exponential/power proposal. Algorithm A uses a tangent transform and rejection predicate. Both loop until accepted.

State/persistence: no module state. Default source relies on libc `drand48()` global RNG state; injected source can use `xi`.

Dependencies/integration: depends on `<math.h>` constants/functions and feeds `fb_random`/randdist behavior used by parser-created random variables and `testrandvar` flowop validation.

Risks: there is no validation for `a <= 0`, null `src`, or invalid uniform outputs outside `(0,1)`. Rejection loops can spin for bad parameters or degenerate random sources. `M_E`/`M_PI` availability depends on platform math definitions.

Test signals: distribution tests should compare sample mean/variance for representative `a` values below, equal to, and above one; source-injection tests should use deterministic uniform sequences and invalid-parameter tests should define expected failure behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/gamma_dist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/gamma_dist.h -->
# sources/test-tools/filebench/gamma_dist.h

Purpose: declares the gamma random sampling interface used by Filebench random distribution code.

Important APIs: `gamma_dist_knuth(double a, double b)` samples using the default libc generator. `gamma_dist_knuth_src(double a, double b, double (*src)(unsigned short *), unsigned short *xi)` lets callers provide a random source compatible with seed arrays.

Control flow contract: callers supply gamma shape `a` and multiplier `b`; the implementation chooses the correct Knuth algorithm by shape.

State/persistence: the header declares stateless functions, but the default implementation depends on global `drand48()` state.

Dependencies/integration: includes `filebench.h` for project context and is expected by random variable machinery.

Risks: no documented preconditions in the header beyond implementation comments; callers must know that `a` must be positive and source functions must return valid uniform doubles.

Test signals: compile checks for random distribution modules and WML `randvar` gamma tests that verify repeatability when seeded through the injected source path.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/gamma_dist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/ioprio.c -->
# sources/test-tools/filebench/ioprio.c

Purpose: optionally sets Linux per-thread/process I/O priority for Filebench worker threads when built with `HAVE_IOPRIO`.

Important APIs/functions: local inline wrappers call `syscall(__NR_ioprio_set)` and `syscall(__NR_ioprio_get)`. `set_thread_ioprio(threadflow_t *tf)` reads `tf->tf_ioprio`, rejects values above 7, sets best-effort class priority, reads back the low priority bits, and logs the result.

Control flow: `flowop_start()` calls `set_thread_ioprio()` before runtime flowop creation. If the syscall fails, the function logs an error and continues without aborting the workload.

State/persistence: changes kernel I/O priority for the current process/thread context. No Filebench shared state is changed beyond logs.

Dependencies/integration: depends on `filebench.h`, `ioprio.h`, AVD evaluation, Linux syscall numbers, and Filebench logging. Header compiles to a no-op when unsupported.

Risks: the implementation hardcodes best-effort class and silently ignores priorities greater than 7. Permission or kernel support failures only log. The syscall target `IOPRIO_WHO_PROCESS, who=0` relies on Linux semantics for current task/process.

Test signals: Linux builds with and without `HAVE_IOPRIO`; WML thread `ioprio` values 0, 7, 8; tests should verify no-op behavior on unsupported platforms and nonfatal logging on permission failure.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/ioprio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/ioprio.h -->
# sources/test-tools/filebench/ioprio.h

Purpose: exposes `set_thread_ioprio()` with a compile-time portability shim.

Important APIs: when `HAVE_IOPRIO` is set, declares the real function and includes Linux syscall definitions. Otherwise defines a static inline no-op accepting `threadflow_t *`.

Control flow: `flowop.c` can call `set_thread_ioprio()` unconditionally because this header erases the feature on unsupported builds.

State/persistence: no-op path has no state; enabled path delegates to `ioprio.c`.

Dependencies/integration: requires `threadflow_t` from prior `filebench.h` inclusion and build-system detection of `HAVE_IOPRIO`.

Risks: the header itself does not include `filebench.h`, so include order matters unless the including C file already has `threadflow_t`. Platform-specific `<asm/unistd.h>` may not expose expected syscall numbers on all Linux variants.

Test signals: compile matrix with `HAVE_IOPRIO` on/off and inclusion from files that have already included `filebench.h`.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/ioprio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/ipc.c -->
# sources/test-tools/filebench/ipc.c

Purpose: implements Filebench shared-memory IPC, shared object allocation, mutex/condition/rwlock attributes, System V semaphore allocation, and optional ISM-style per-thread memory pools.

Important APIs/functions: `ipc_init()` creates and mmaps a temporary shared-memory file, zeroes pre-pool state, initializes locks/conds/rwlocks, sets defaults, and prepares semaphore keys. `ipc_attach()` maps a worker process at the master-supplied address. `ipc_malloc()`/`ipc_free()` allocate typed objects from fixed pools tracked by bitmaps. `ipc_stralloc()`, `ipc_pathalloc()`, and `ipc_cvar_heapalloc()` allocate from linear shared buffers. `ipc_seminit()`, `ipc_semidalloc()`, and `ipc_semidfree()` manage shared semaphores. `ipc_ismcreate()`, `ipc_ismmalloc()`, and `ipc_ismdelete()` manage a separate shared memory segment.

Control flow: master calls `ipc_init()` before parser and object definitions; worker processes call `ipc_attach()` and then use the already-initialized shared state. Allocators lock `shm_malloc_lock`, scan type-specific bitmaps from the last index, zero the selected object, and return typed pool addresses.

State/persistence: `filebench_shm` points to `filebench_shm_t`, a large shared object containing global lists, locks, counters, fixed pools, bitmaps, string/path heaps, cvar heap, eventgen state, run flags, and plugin selection. Shared-memory files are created under `/tmp` with generated suffixes and unlinked in `ipc_fini()`.

Dependencies/integration: central to fileset/procflow/threadflow/flowop/variable/randdist/cvar allocation. Integrates with `misc.c` logging, parser lifecycle, proc worker exec, flowop synchronization, and platform pthread/process-shared/robust mutex features.

Risks: pool sizes are fixed compile-time limits; exhaustion often aborts. `ipc_stralloc()`/`ipc_pathalloc()` use `strncpy()` for `strlen()` bytes and rely on prezeroed memory for null termination. `ipc_free()` does little bounds validation. `ipc_ismmalloc()` has an explicit no-out-of-memory check comment. Mapping workers at exactly the master's address is fragile under ASLR, hence parser startup disables ASLR.

Test signals: master/worker attach smoke tests, pool exhaustion tests for each object type, robust mutex behavior after owner death, semaphore allocation exhaustion, string/path heap boundaries, and ISM allocation with multiple worker processes.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/ipc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/ipc.h -->
# sources/test-tools/filebench/ipc.h

Purpose: defines the shared-memory schema and IPC constants used across Filebench. It is the contract for all global state, object pools, run modes, abort reasons, mutex attributes, and IPC helper APIs.

Important APIs/types: `filebench_shm_t` contains global fileset/procflow/flowop lists and locks, parallel allocation controls, process/run abort state, parser variables, random/custom variable lists, logging/dump settings, eventgen queue, System V semaphore ids, run/misc modes, shared string/path/cvar heaps, ISM allocation pointers, filesystem plugin type, pool bitmaps, last allocation indices, and fixed arrays for every allocatable object. Public functions expose initialization, attach/fini, allocation/free, mutex/cond attributes, semids, strings/paths/cvar heap, mutex wrappers, sem init, and ISM operations.

Control flow contract: master creates and initializes `filebench_shm`; worker processes attach to it. Object modules use `ipc_malloc(type)` and `ipc_free(type, addr)` rather than heap allocation for shared objects. The marker field divides zeroed metadata from nonzeroed large pools during `ipc_init()`.

State/persistence: the header fixes capacities such as filesets, entries, procflows, threadflows, flowops, variables, AVDs, randdists, cvars, string memory, path memory, and cvar heap size. Runtime state persists only for the benchmark process lifetime in mmap/shared memory.

Dependencies/integration: includes `filebench.h` and references most core structs. `shm_filesys_type` connects to `fsplug.h`; run/abort flags are interpreted by parser/procflow/flowop loops.

Risks: changing pool sizes affects shared memory footprint and ABI. The bitmap dimensions use `FILEBENCH_MAXBITMAP`, driven by file entries, for every type, which is simple but large. Typo-prone integer constants are shared across modules and must remain synchronized with allocation switch statements.

Test signals: compile checks for allocation switch coverage when adding a new object type, shared-memory size sanity, and full workload tests that allocate near configured maxima.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/ipc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/misc.c -->
# sources/test-tools/filebench/misc.c

Purpose: provides central logging and process shutdown behavior for Filebench.

Important APIs/functions: `filebench_log(level, fmt, ...)` writes formatted messages to stdout, stderr, or the configured dump file, honoring debug level, `LOG_ERROR1` suppression, `LOG_DUMP`, timestamps relative to `shm_epoch`, and shared `shm_msg_lock` serialization. `filebench_shutdown(error)` marks abort state on error, calls `procflow_shutdown()`, unlinks legacy `/tmp/filebench_shm`, deletes ISM, and exits.

Control flow: logging can be called before `filebench_shm` exists, in which case it treats messages as fatal and prints to stderr. Normal messages are filtered by `shm_debug_level`; dump messages lazily open/truncate `shm_dump_filename` and fsync after each write. Shutdown distinguishes repeated finalization from fresh error aborts using `shm_f_abort`.

State/persistence: uses `filebench_shm` for debug level, dump fd/name, first-error suppression, message lock, epoch, and abort state. Dump files persist on disk if configured; shared memory and ISM are cleaned on shutdown paths.

Dependencies/integration: depends on IPC mutex wrappers, timing helpers, `procflow_shutdown()`, `eventgen`/filesystem includes, and parser line number `lex_lineno` for pre-run syntax errors.

Risks: uses `vsprintf()` into a fixed 128 KiB buffer instead of bounded `vsnprintf()`. Dump file writes ignore write failures except open failure. Shutdown unlinks a hardcoded `/tmp/filebench_shm` path that differs from generated `shmpath` cleanup handled elsewhere.

Test signals: logging before and after `ipc_init()`, debug-level filtering, dump file creation, `LOG_ERROR1` suppression, concurrent logging from workers, and shutdown after both normal and error abort states.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/misc.h -->
# sources/test-tools/filebench/misc.h

Purpose: defines Filebench logging level constants.

Important APIs/constants: `LOG_ERROR`, `LOG_ERROR1`, `LOG_INFO`, `LOG_VERBOSE`, `LOG_DEBUG_SCRIPT`, `LOG_DEBUG_IMPL`, `LOG_DEBUG_NEVER`, `LOG_FATAL`, and `LOG_DUMP` classify output routing and filtering in `filebench_log()`.

Control flow contract: levels below info route to stderr, normal info/debug route to stdout when enabled, fatal can be used before shared memory exists, and dump writes to the configured dump fd.

State/persistence: constants only; behavior depends on `filebench_shm->shm_debug_level`, dump state, and error suppression.

Dependencies/integration: included via project headers wherever logging occurs.

Risks: numeric values are part of implicit filtering semantics; adding intermediate values can change what existing debug settings emit.

Test signals: unit/smoke tests should assert each level's route/filter behavior through `filebench_log()`.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/misc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/multi_client_sync.c -->
# sources/test-tools/filebench/multi_client_sync.c

Purpose: implements a simple TCP client for coordinating multi-client Filebench runs with an external synchronization master.

Important APIs/functions: `mc_sync_open_sock(master_name, master_port, my_name)` stores the client name, creates a TCP socket, binds locally, resolves the master with `gethostbyname()`, and connects. `mc_sync_synchronize(sync_point)` sends a `cmd=SYNC` message including client name and sample number, then waits for a newline-terminated reply.

Control flow: parser command `enable multi` opens the socket, and `domultisync` calls synchronize at WML-defined points. Success is logged and `FILEBENCH_OK` is returned; socket/bind/connect errors log and return `FILEBENCH_ERROR`.

State/persistence: static `mc_sync_sock_id` and `this_client_name` persist for the process. The socket remains open for later sync points.

Dependencies/integration: uses BSD sockets, DNS, parser multi-client commands, Filebench logging/status constants, and `multi_client_sync.h`.

Risks: no null check after `gethostbyname()`. `strncpy()` may leave `this_client_name` unterminated for long names. The receive loop repeatedly writes at the start of `msg`, does not reserve space for a terminator, does not handle `recv()` returning 0/-1, and can spin or overcount. Socket is not closed.

Test signals: integration with a fake sync server, DNS failure, refused connection, partial replies, missing newline, long client names, and repeated sync points.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/multi_client_sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/multi_client_sync.h -->
# sources/test-tools/filebench/multi_client_sync.h

Purpose: declares the multi-client synchronization client API.

Important APIs: `mc_sync_open_sock(char *master_name, int master_port, char *client_name)` establishes the TCP connection. `mc_sync_synchronize(int synch_point)` blocks until the external master releases a sync point.

Control flow contract: parser code calls open before synchronize; callers receive Filebench status codes.

State/persistence: implementation stores one static socket/client identity per process.

Dependencies/integration: conditionally includes socket headers based on configuration and is used by `parser_gram.y`.

Risks: the API does not expose close/reset, timeout, or error detail, which limits recovery after sync server failure.

Test signals: compile with/without `HAVE_SYS_SOCKET_H` and parser-level WML tests for `enable multi` plus `domultisync`.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/multi_client_sync.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/parser_gram.y -->
# sources/test-tools/filebench/parser_gram.y

Purpose: defines the yacc grammar, command callbacks, option parsing, and `main()` entry point for Filebench's Workload Model Language interpreter.

Important APIs/functions: grammar rules build `cmd_t`, `attr_t`, `list_t`, and `probtabent_t` structures for commands including `define`, `create`, `run`, `psrun`, `set`, `eventgen`, `enable multi`, `domultisync`, `system`, `echo`, `sleep`, `list`, `version`, and `quit`. Callback functions instantiate procflows, threadflows, flowops, composite flowops, files/filesets, random variables, and custom variables. `parse_options()` selects help, master, worker, or custom-variable listing modes; `master_mode()` initializes IPC, flowops, eventgen, cvars, and invokes `yyparse()`; `worker_mode()` attaches to shared memory and executes a procflow.

Control flow: lexer tokens feed grammar productions. Completed commands execute immediately in the top-level `commands` rule. Master mode parses WML and typically exits through `run`/`psrun` shutdown; worker mode is invoked by master with private `-a/-s/-m/-i` parameters. Composite flowops are defined as flowop trees with local variable attributes propagated into inner flowops.

State/persistence: command and attribute nodes are heap allocated during parsing; durable benchmark objects are allocated in shared memory through fileset/procflow/threadflow/flowop/var/cvar APIs. `execname` stores the executable path for worker exec. Global `filebench_shm` records run modes, debug flags, lathist enablement, and script name.

Dependencies/integration: ties together almost every subsystem: parser lexer, variables/AVDs, filesets, flowops, procflows, eventgen, stats, IPC, cvar libraries, ASLR control, multi-client sync, and platform resource setup.

Risks: commands execute while parsing, so syntax accepted before a later parse error may already mutate shared state. Attribute lookup returns the last matching attribute without duplicate diagnostics. Many parser errors call `filebench_shutdown(1)`. `system` intentionally executes shell commands from WML. Composite/local variable handling depends on shared local-variable list manipulation.

Test signals: parser tests for every command form and attribute; malformed WML recovery; master/worker command-line modes; composite flowop local variables; random/cvar definitions; run modes (`timeout`, `firstdone`, `alldone`, `nousestats`); periodic stats; and no-run warning behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/parser_gram.y -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/parser_lex.l -->
# sources/test-tools/filebench/parser_lex.l

Purpose: defines the flex lexer for Filebench WML. It tokenizes commands, entity names, attributes, random-variable keywords, literals, variables, quoted strings, punctuation, comments, and whitespace.

Important APIs/functions: returns tokens declared in `parser_gram.y`, fills `yylval` fields for integers, booleans, strings, variables, and quoted string fragments, tracks `lex_lineno`, reports syntax errors through `yyerror()`, and exposes `yy_switchfileparent()`/`yy_switchfilescript()` buffer helpers.

Control flow: in `INITIAL` state it ignores spaces/tabs/comments, increments line count, recognizes keywords before generic strings, parses numeric suffixes `k`, `m`, `g` into byte-scaled integers, and enters `WHITESTRINGSTATE` on quotes. Quoted strings are returned as a sequence of `FSV_WHITESTRING` or variable tokens until the closing quote.

State/persistence: global `lex_lineno` persists for diagnostics. Flex buffer globals `parent` and `script` support switching input buffers. The lexer allocates token strings with `strdup()`; parser callbacks convert them into AVD/string storage.

Dependencies/integration: includes `filebench.h`, parser types, generated grammar header, and utility macros such as `KB`, `MB`, `GB`. Calls `filebench_shutdown()` on allocation failure.

Risks: token rules are order-sensitive; new keywords must precede generic string matching. Variable and string regexes are restrictive and may reject valid-looking paths or names. Numeric scaling can overflow before `errno` catches all cases because multiplication happens after conversion. Quoted-string handling has several special cases for `$`, backslash, and newline escapes that need regression coverage.

Test signals: lexer tests for every keyword, comments, line numbers, quoted strings with variables and escaped newline/dollar, integer suffixes, negative integers, booleans, path-like strings, illegal characters, and parser buffer switching.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/parser_lex.l -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/parsertypes.h -->
# sources/test-tools/filebench/parsertypes.h

Purpose: defines parser-side data structures passed from yacc grammar productions to command execution callbacks.

Important APIs/types: `list_t` stores string/integer AVD pairs for quoted/string parameter lists. `attr_t` stores an attribute token id, linked-list pointer, AVD value, or object pointer such as a probability table. `cmd_t` stores callback pointer, command/entity names, quantities, nested command lists, attribute lists, and parameter lists. `fs_u` is a small semantic-value union. `pidlist_t` tracks child process fd/pid pairs. `cmdfunc` names command callback signatures. It declares lexer buffer switch helpers.

Control flow contract: grammar productions allocate these nodes, link them in source order, and command callbacks traverse them to create Filebench runtime objects.

State/persistence: these structures are mostly transient heap parser state, while their AVDs may reference shared variables or shared-memory allocations.

Dependencies/integration: includes `filebench.h` for `avd_t` and project types; token ids come from grammar definitions.

Risks: generic fields make ownership unclear. Some command nodes are freed at top level, but nested lists/attrs/strings have partial cleanup, so parser lifetime assumes short process runs. Attribute ids are plain ints, so misuse is detected only by command-specific logic.

Test signals: parser memory/debug tests for nested process/thread/flowop definitions, composite local variables, parameter lists, and random probability-table objects.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/parsertypes.h -->
