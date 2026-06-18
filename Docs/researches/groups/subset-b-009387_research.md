# subset-b-009387 research

Grouped research report for the requested stress-ng subset. Each section preserves the source path and is bounded for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-xattr.c -->
# sources/test-tools/stress-ng/stress-xattr.c

Purpose: implements the `xattr` stressor, exercising file extended attribute creation, replacement, lookup, listing, and removal paths through descriptor, pathname, symlink-oriented, and newer `*xattrat` wrappers where available.

Important APIs/types/functions: `stress_xattr`, `stress_xattr_info`, `stress_help_t`, `stress_fs_temp_dir_make_args`, `stress_fs_temp_filename_args`, `stress_fs_type_get`, `stress_fs_bad_fd_get`, `shim_fsetxattr`, `shim_setxattr`, optional `shim_lsetxattr` and `shim_setxattrat`, `shim_fgetxattr`, `shim_getxattr`, optional `shim_lgetxattr`, `shim_flistxattr`, `shim_listxattr`, optional `shim_llistxattr` and `shim_listxattrat`, `shim_fremovexattr`, `shim_removexattr`, optional `shim_lremovexattr` and `shim_removexattrat`, `XATTR_CREATE`, `XATTR_REPLACE`, `XATTR_SIZE_MAX`, and the stress-ng bitset helpers used to remember which attributes were actually created.

Control flow: the stressor creates a temporary directory and regular file, allocates optional over-sized value buffers, opens the file, records the filesystem type for diagnostics, then enters the synchronized run loop. Each iteration tries to create up to `MAX_XATTRS` `user.var_N` attributes, handles no-support/no-space quota cases distinctly, probes zero-length values, invalid descriptors, invalid flags, missing names, invalid attribute names, and oversized values. It then verifies that replacing a missing attribute fails, verifies duplicate `XATTR_CREATE` fails for existing attributes, replaces successfully-created attributes by fd/path/optional link and `setxattrat` APIs, reads values back through fd/path/optional link APIs, lists xattrs after sizing the list buffer, exercises invalid list requests, removes attributes through a rotation of removal APIs, probes invalid remove cases and long names, optionally exercises `O_TMPFILE` xattr replacement behavior, and increments bogo operations. Cleanup closes the fd, unlinks the file, removes the temp directory, frees buffers, and returns either success, no-resource skip, or failure.

State and persistence behavior: persistent filesystem state is limited to a stress-ng temporary directory, one regular file, optional anonymous `O_TMPFILE`, and many transient `user.*` xattrs. In-memory state includes the `set_xattr_ok` bitset, path buffers, huge value buffers, and loop-local value buffers. All intended persistent objects are removed on normal exits and most failure paths.

Dependencies and integration points: enabled only when an xattr header and the required xattr family calls are detected; otherwise `stress_xattr_info` points to `stress_unimplemented`. It integrates with stress-ng temp-file helpers, syscall shim wrappers, process state transitions, bogo accounting, filesystem type reporting, memory-free diagnostics, and `CLASS_FILESYSTEM | CLASS_OS` registration with `VERIFY_ALWAYS`.

Risks and test signals: behavior is filesystem-dependent; `ENOTSUP`, `ENOSYS`, `ENOSPC`, `EDQUOT`, `E2BIG`, and platform absence are expected in some environments. The stressor flags unexpected success for invalid flags, replacement of non-existent attributes, duplicate create, or oversize values, and unexpected read/list/remove failures or value mismatches. Resource pressure can skip or shorten coverage; cleanup mistakes would leave temp files or attributes behind.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-xattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-yield.c -->
# sources/test-tools/stress-ng/stress-yield.c

Purpose: implements the `yield` scheduler stressor, creating child yielder processes that repeatedly call `sched_yield()` and optionally run under selected scheduler policies to measure yield latency and drive context switching.

Important APIs/types/functions: `stress_yield`, `stress_yield_sched_policy`, `stress_yield_sched`, `stress_yield_info`, `stress_sched_types`, `sched_getaffinity`, `sched_setscheduler`, `sched_get_priority_min`, `sched_get_priority_max`, optional `sched_rr_get_interval`, optional `shim_sched_setattr` for `SCHED_DEADLINE`, `shim_sched_yield`, `shim_rseq_slice_yield`, `stress_kill_and_wait_many`, `stress_metrics_t`, and settings `yield-procs` and `yield-sched`.

Control flow: option parsing chooses an explicit yielder count or computes roughly two yielders per available CPU divided across stressor instances, with affinity masks reducing the CPU count when available. The parent allocates a child pid array and shared anonymous metrics mapping, synchronizes with other workers, then forks the yielder children. Each child applies normal stress-ng child setup, optional scheduler policy changes, repeatedly times `shim_sched_yield`, accumulates count and duration in its metrics slot, optionally reports verify failures, calls the rseq slice yield shim, and exits when the global stop or per-child bogo limit is reached. The parent sleeps/yields while the stressor runs, kills and waits for children, aggregates metrics, adds bogo operations, publishes nanoseconds per `sched_yield`, unmaps shared metrics, and frees pids.

State and persistence behavior: state is entirely process-local or shared anonymous memory: child pid slots and per-child metrics. Scheduler policy changes affect only participating processes and do not persist after exit. No files or external persistent state are created.

Dependencies and integration points: compiled only with scheduler/affinity support and at least one known scheduling policy on supported operating systems. It uses stress-ng setting lookup, synchronization, child failure injection, parent-death alarms, scheduler settings, metrics publication, kill/wait helpers, and registers as `CLASS_SCHEDULER | CLASS_OS` with optional verification.

Risks and test signals: scheduler policy application can fail for privilege or kernel support reasons and is mostly diagnostic. Fork or mapping failures skip with no-resource status. Verification reports unexpected `sched_yield` errors. High `yield-procs` can create many children, stress scheduler fairness, and interact with CPU affinity or realtime/deadline policies.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-yield.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-zero.c -->
# sources/test-tools/stress-ng/stress-zero.c

Purpose: implements the `zero` stressor, exercising `/dev/zero` reads, optional writes, Linux mmap behavior, lseek, and ioctl paths while verifying that bytes read or mapped from the device are zero.

Important APIs/types/functions: `stress_zero`, `stress_zero_info`, `mmap_flags_t`, `mmap_flags`, `stress_mmap_populate`, `stress_madvise_mergeable`, `stress_data_is_not_zero`, `stress_munmap_force`, `open`, `read`, optional `write`, `mmap`, `munmap`, `lseek`, `ioctl`, `FIONBIO`, `FIONREAD`, `FIGETBSZ`, and option `zero-read`.

Control flow: the stressor maps page-sized read and write buffers, opens `/dev/zero` read/write except on Minix, synchronizes, and either runs a read-only benchmark loop or the broader exercise loop. Read-only mode continuously reads one page, counts bytes and bogo operations, and validates the final buffer. Full mode batches reads, verifies zero data, writes a page where supported, periodically mmaps `/dev/zero` with rotating anonymous/private/shared/locked/populate flag combinations on Linux and verifies mapped zeros, performs several lseek probes, toggles nonblocking ioctl state where available, probes read-size and block-size ioctls, and increments bogo operations. It closes the device, unmaps buffers, and publishes MB/sec read rate.

State and persistence behavior: state is limited to two anonymous page buffers, an open `/dev/zero` descriptor, byte counters, timing totals, and temporary Linux mappings. No persistent files are created and `/dev/zero` itself has no retained content.

Dependencies and integration points: uses stress-ng mmap, madvise, memory naming, metrics, option parsing, synchronization, and process-state helpers. Linux-specific mmap flag cycling is guarded by `__linux__`; Minix uses read-only open flags. The stressor registers as `CLASS_DEV | CLASS_MEMORY | CLASS_OS` with always-on verification.

Risks and test signals: failures include inability to open or read `/dev/zero`, non-zero data from reads or mappings, unexpected mmap failures other than transient memory pressure, and write/ioctl errors outside tolerated transient cases. Metrics can be skewed in full mode because mmap/ioctl/lseek work is interleaved with reads; `--zero-read` isolates read throughput.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-zero.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-zlib.c -->
# sources/test-tools/stress-ng/stress-zlib.c

Purpose: implements the `zlib` stressor, generating many data patterns, deflating them through zlib in a parent process, inflating them in a child process via a pipe, and optionally verifying checksums across the compressed/decompressed stream.

Important APIs/types/functions: `stress_zlib`, `stress_zlib_deflate`, `stress_zlib_inflate`, `stress_zlib_get_args`, `stress_zlib_window_bits`, `stress_zlib_err`, `stress_zlib_random_test`, `stress_zlib_method_t`, `stress_zlib_checksum_t`, `stress_zlib_shared_checksums_t`, `stress_zlib_args_t`, `zlib_rand_data_methods`, many `stress_rand_data_*` generators, `deflateInit2`, `deflate`, `deflateEnd`, `inflateInit2`, `inflate`, `inflateEnd`, `z_stream`, `pipe`, `fork`, shared anonymous mmap, `SIGPIPE`, `sigsetjmp`/`siglongjmp`, and settings for level, mem level, method, strategy, window bits, and stream bytes.

Control flow: option helpers validate zlib window-bit ranges and gather defaults or stress-ng maximize/minimize overrides. `stress_zlib` installs signal handling, maps shared checksum state, creates a pipe, synchronizes, forks an inflater child pinned near the parent CPU, and runs deflation in the parent. The parent repeatedly initializes a deflate stream, generates 64 KiB input blocks using the selected data generator, optionally accumulates input checksum/byte counts, deflates into 64 KiB output blocks, sends each compressed block length and payload through the pipe, and records compression ratio/rate metrics. The child repeatedly initializes an inflate stream, reads each length-prefixed compressed block, inflates to output buffers, and optionally accumulates output checksum/byte counts. After the pipe closes, the parent waits for the child, merges error/interruption/broken-pipe flags, compares checksums under verify mode, unmaps shared state, and kills/waits defensively.

State and persistence behavior: persistent state is not created. Runtime state includes static aligned input/output buffers, many data generator static seeds or phase variables, `pipe_broken`, `jmp_env` for guarded object-code reads, per-process zlib streams, shared checksums, pipe descriptors, and metrics counters. Static generator state intentionally persists within a worker process across generated blocks to vary patterns.

Dependencies and integration points: compiled only with `HAVE_LIB_Z` and `HAVE_SIGLONGJMP`; otherwise it registers as unimplemented. It integrates with stress-ng CPU affinity, architecture helpers, x86 random instruction helpers, target clones, signal shims, mmap helpers, scheduler setup, parent-death alarms, bogo accounting, metrics, and classes `CLASS_CPU | CLASS_CPU_CACHE | CLASS_MEMORY | CLASS_COMPUTE`.

Risks and test signals: invalid zlib parameter combinations surface as `Z_STREAM_ERROR`; memory or version problems use zlib error mapping. Pipe interruptions and broken pipes can prevent checksum verification without necessarily meaning data corruption. The object-code generator can fault on unreadable text pages and falls back to binary data through SIGSEGV/SIGBUS recovery. Verify mode catches checksum mismatches between deflated input and inflated output; metrics expose compression ratio, throughput, and compressed volume.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-zlib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-zombie.c -->
# sources/test-tools/stress-ng/stress-zombie.c

Purpose: implements the `zombie` stressor, rapidly creating child processes that exit into zombie state, optionally using Linux `clone` namespace flags, then reaping them under a configurable per-worker maximum.

Important APIs/types/functions: `stress_zombie`, `stress_zombie_child`, optional `stress_zombie_clone` and `stress_zombie_clone_cap_sys_admin`, `stress_pid_a_zombie`, `stress_zombie_new`, `stress_zombie_head_remove`, `stress_zombie_free`, `stress_zombie_t`, `stress_zombie_list_t`, `stress_zombie_context_t`, `fork`, optional `clone`, `waitpid`, `setpgid`, `/proc/PID/stat` parsing, `stress_capabilities_check`, `stress_kill_pid`, and options `zombie-max` and `zombie-clone`.

Control flow: option parsing selects zombie maximum and clone mode; clone mode is downgraded when unavailable or when `CAP_SYS_ADMIN` is missing. On Linux clone builds it prepares a temporary context path. After synchronization, the main loop allocates or reuses a zombie list node, creates a child by fork or clone, lets the child mark zombie state and exit, records the pid, sets process group, tracks maximum list length, and increments bogo operations. When the configured zombie limit is reached or process creation fails, the head zombie is optionally verified as zombie state and reaped. Shutdown records the maximum zombies metric, reaps all remaining children, frees active and free-list nodes, and removes the temporary path.

State and persistence behavior: global state is the `zombies` active/free linked lists and `zombie_clone` option flag. Each active node stores pid and optional clone stack. Child process table entries persist as zombies only until the parent reaps them. The optional temporary path is removed during cleanup.

Dependencies and integration points: Linux clone namespace coverage is conditional on `clone` and namespace flags; otherwise fork is used. The stressor integrates with stress-ng process state, capability checks, temp path helpers, kill/wait shims, bogo accounting, metrics, and registers as `CLASS_SCHEDULER | CLASS_OS` with optional verification.

Risks and test signals: high `zombie-max` can hit process limits and force reap/retry behavior. `/proc` verification can be inconclusive, so unknown state is treated conservatively. Clone namespace mode may require `CAP_SYS_ADMIN`; the clone child can intentionally leak a socket to exercise namespace/network cleanup. Verification reports pids that never appear as zombies before reaping.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-zombie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/config.h -->
# sources/test-tools/stress-ng/test/config.h

Purpose: central lightweight configuration header for stress-ng compile probes in this `test/` directory. It supplies fallback feature definitions so individual probes can compile in isolation while still matching stress-ng's autoconf-style expectations.

Important APIs/types/functions: preprocessor feature macros; includes: no external include beyond compiler defaults; defined macros include none.

Control flow: there is no runtime control flow. The file is included by small probe programs when they need common feature shims or neutral defaults before checking a platform API, compiler builtin, type, attribute, or instruction.

State and persistence behavior: no runtime state and no persistent state; it only affects preprocessing and compilation.

Dependencies and integration points: integrated with the stress-ng build feature-detection tests. Any macro here can change whether a probe compiles and therefore whether the main stress-ng build enables corresponding guarded code.

Risks and test signals: incorrect definitions can produce false-positive or false-negative feature detection. The signal is successful preprocessing/compilation of dependent tests rather than runtime behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-__restrict.c -->
# sources/test-tools/stress-ng/test/test-__restrict.c

Purpose: compile probe for the `__restrict` qualifier so stress-ng can use restricted pointer annotations in hot helper functions without breaking compilers that lack the spelling.

Important APIs/types/functions: `__restrict` pointer-qualified parameters or locals; observed symbols: `test`; includes: no external include beyond compiler defaults; macros: none.

Control flow: the probe calls a small function or expression using restricted pointers and exits. Runtime behavior is only present to force type checking.

State and persistence behavior: no persistent state; local variables or arrays exist only during the probe.

Dependencies and integration points: informs portability macros used across stress-ng for aliasing assumptions and optimization hints.

Risks and test signals: compilers may support standard `restrict` but not `__restrict`, or only in certain language modes. Clean compilation is the signal.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-__restrict.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-__rolb.c -->
# sources/test-tools/stress-ng/test/test-__rolb.c

Purpose: compile probe for compiler rotate intrinsic `__rolb`, checking availability of a left rotate on byte-sized operands.

Important APIs/types/functions: intrinsic call `__rolb`; observed symbols: `__rolb`; includes: `<stdint.h>`, `<x86intrin.h>`; macros: none.

Control flow: `main` creates a local integer value, invokes the rotate intrinsic, and returns a value derived from the result. There are no branches beyond any compiler or platform guards.

State and persistence behavior: state is limited to local scalar variables. No persistent resources are created.

Dependencies and integration points: enables stress-ng rotate helpers or optimized bit-manipulation paths where compiler intrinsics are available. Without it, portable shift/or fallbacks remain necessary.

Risks and test signals: rotate intrinsic names are compiler-specific and may exist only for particular targets or modes. Successful compilation is the feature signal, not a broad arithmetic validation suite.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-__rolb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-__rold.c -->
# sources/test-tools/stress-ng/test/test-__rold.c

Purpose: compile probe for compiler rotate intrinsic `__rold`, checking availability of a left rotate on doubleword-sized operands.

Important APIs/types/functions: intrinsic call `__rold`; observed symbols: `__rold`; includes: `<stdint.h>`, `<x86intrin.h>`; macros: none.

Control flow: `main` creates a local integer value, invokes the rotate intrinsic, and returns a value derived from the result. There are no branches beyond any compiler or platform guards.

State and persistence behavior: state is limited to local scalar variables. No persistent resources are created.

Dependencies and integration points: enables stress-ng rotate helpers or optimized bit-manipulation paths where compiler intrinsics are available. Without it, portable shift/or fallbacks remain necessary.

Risks and test signals: rotate intrinsic names are compiler-specific and may exist only for particular targets or modes. Successful compilation is the feature signal, not a broad arithmetic validation suite.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-__rold.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-__rolq.c -->
# sources/test-tools/stress-ng/test/test-__rolq.c

Purpose: compile probe for compiler rotate intrinsic `__rolq`, checking availability of a left rotate on quadword-sized operands.

Important APIs/types/functions: intrinsic call `__rolq`; observed symbols: `__rolq`; includes: `<stdint.h>`, `<x86intrin.h>`; macros: none.

Control flow: `main` creates a local integer value, invokes the rotate intrinsic, and returns a value derived from the result. There are no branches beyond any compiler or platform guards.

State and persistence behavior: state is limited to local scalar variables. No persistent resources are created.

Dependencies and integration points: enables stress-ng rotate helpers or optimized bit-manipulation paths where compiler intrinsics are available. Without it, portable shift/or fallbacks remain necessary.

Risks and test signals: rotate intrinsic names are compiler-specific and may exist only for particular targets or modes. Successful compilation is the feature signal, not a broad arithmetic validation suite.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-__rolq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-__rolw.c -->
# sources/test-tools/stress-ng/test/test-__rolw.c

Purpose: compile probe for compiler rotate intrinsic `__rolw`, checking availability of a left rotate on word-sized operands.

Important APIs/types/functions: intrinsic call `__rolw`; observed symbols: `__rolw`; includes: `<stdint.h>`, `<x86intrin.h>`; macros: none.

Control flow: `main` creates a local integer value, invokes the rotate intrinsic, and returns a value derived from the result. There are no branches beyond any compiler or platform guards.

State and persistence behavior: state is limited to local scalar variables. No persistent resources are created.

Dependencies and integration points: enables stress-ng rotate helpers or optimized bit-manipulation paths where compiler intrinsics are available. Without it, portable shift/or fallbacks remain necessary.

Risks and test signals: rotate intrinsic names are compiler-specific and may exist only for particular targets or modes. Successful compilation is the feature signal, not a broad arithmetic validation suite.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-__rolw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-__rorb.c -->
# sources/test-tools/stress-ng/test/test-__rorb.c

Purpose: compile probe for compiler rotate intrinsic `__rorb`, checking availability of a right rotate on byte-sized operands.

Important APIs/types/functions: intrinsic call `__rorb`; observed symbols: `__rorb`; includes: `<stdint.h>`, `<x86intrin.h>`; macros: none.

Control flow: `main` creates a local integer value, invokes the rotate intrinsic, and returns a value derived from the result. There are no branches beyond any compiler or platform guards.

State and persistence behavior: state is limited to local scalar variables. No persistent resources are created.

Dependencies and integration points: enables stress-ng rotate helpers or optimized bit-manipulation paths where compiler intrinsics are available. Without it, portable shift/or fallbacks remain necessary.

Risks and test signals: rotate intrinsic names are compiler-specific and may exist only for particular targets or modes. Successful compilation is the feature signal, not a broad arithmetic validation suite.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-__rorb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-__rord.c -->
# sources/test-tools/stress-ng/test/test-__rord.c

Purpose: compile probe for compiler rotate intrinsic `__rord`, checking availability of a right rotate on doubleword-sized operands.

Important APIs/types/functions: intrinsic call `__rord`; observed symbols: `__rord`; includes: `<stdint.h>`, `<x86intrin.h>`; macros: none.

Control flow: `main` creates a local integer value, invokes the rotate intrinsic, and returns a value derived from the result. There are no branches beyond any compiler or platform guards.

State and persistence behavior: state is limited to local scalar variables. No persistent resources are created.

Dependencies and integration points: enables stress-ng rotate helpers or optimized bit-manipulation paths where compiler intrinsics are available. Without it, portable shift/or fallbacks remain necessary.

Risks and test signals: rotate intrinsic names are compiler-specific and may exist only for particular targets or modes. Successful compilation is the feature signal, not a broad arithmetic validation suite.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-__rord.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-__rorq.c -->
# sources/test-tools/stress-ng/test/test-__rorq.c

Purpose: compile probe for compiler rotate intrinsic `__rorq`, checking availability of a right rotate on quadword-sized operands.

Important APIs/types/functions: intrinsic call `__rorq`; observed symbols: `__rorq`; includes: `<stdint.h>`, `<x86intrin.h>`; macros: none.

Control flow: `main` creates a local integer value, invokes the rotate intrinsic, and returns a value derived from the result. There are no branches beyond any compiler or platform guards.

State and persistence behavior: state is limited to local scalar variables. No persistent resources are created.

Dependencies and integration points: enables stress-ng rotate helpers or optimized bit-manipulation paths where compiler intrinsics are available. Without it, portable shift/or fallbacks remain necessary.

Risks and test signals: rotate intrinsic names are compiler-specific and may exist only for particular targets or modes. Successful compilation is the feature signal, not a broad arithmetic validation suite.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-__rorq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-__rorw.c -->
# sources/test-tools/stress-ng/test/test-__rorw.c

Purpose: compile probe for compiler rotate intrinsic `__rorw`, checking availability of a right rotate on word-sized operands.

Important APIs/types/functions: intrinsic call `__rorw`; observed symbols: `__rorw`; includes: `<stdint.h>`, `<x86intrin.h>`; macros: none.

Control flow: `main` creates a local integer value, invokes the rotate intrinsic, and returns a value derived from the result. There are no branches beyond any compiler or platform guards.

State and persistence behavior: state is limited to local scalar variables. No persistent resources are created.

Dependencies and integration points: enables stress-ng rotate helpers or optimized bit-manipulation paths where compiler intrinsics are available. Without it, portable shift/or fallbacks remain necessary.

Risks and test signals: rotate intrinsic names are compiler-specific and may exist only for particular targets or modes. Successful compilation is the feature signal, not a broad arithmetic validation suite.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-__rorw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-__rseq_offset.c -->
# sources/test-tools/stress-ng/test/test-__rseq_offset.c

Purpose: compile probe for restartable-sequence offset support, checking whether the toolchain and system headers expose `__rseq_offset` or compatible symbols used by stress-ng rseq helpers.

Important APIs/types/functions: rseq offset symbol access; observed symbols: `main` only with compile-time expressions; includes: `<stddef.h>`; macros: none.

Control flow: `main` references the rseq offset symbol and returns a simple value. The code is intentionally small so missing TLS/libc exposure fails at compile or link time.

State and persistence behavior: no persistent state. It only reads or references process/thread metadata exposed by the C library or kernel headers.

Dependencies and integration points: used to decide whether stress-ng can compile rseq slice/yield helpers and related scheduler instrumentation.

Risks and test signals: rseq support varies by libc, kernel headers, architecture, and link mode. Successful compilation/linking does not prove the running kernel has enabled rseq for the process.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-__rseq_offset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-accept4.c -->
# sources/test-tools/stress-ng/test/test-accept4.c

Purpose: compile probe for accept4 with `SOCK_NONBLOCK | SOCK_CLOEXEC`. It exists to let the stress-ng build detect whether this platform exposes the API, type, constant, header, or library call needed by guarded stressor code.

Important APIs/types/functions: observed call/type/function symbols include `accept4`; includes: `<sys/types.h>`, `<sys/socket.h>`; macros: `_GNU_SOURCE`.

Control flow: `main` declares minimal arguments, invokes or references the target API/type, and returns the result or zero. Invalid descriptors, null-ish arguments, or dummy structures are acceptable because compile/link availability is the primary goal.

State and persistence behavior: any state is local to the probe process. The file does not intentionally create durable resources; when it opens or allocates anything, the scope is limited to proving the symbol and signature are usable.

Dependencies and integration points: this probe contributes one feature bit to stress-ng's generated configuration, enabling or disabling code paths that use `accept4`. Some probes also require external libraries such as libacl, libbsd, libc realtime/AIO support, or platform-specific headers.

Risks and test signals: successful compilation may not imply the call succeeds at runtime with dummy arguments, sufficient privileges, or all kernels. Failures indicate missing headers, declarations, libraries, constants, or incompatible signatures.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-accept4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-acct-v3.c -->
# sources/test-tools/stress-ng/test/test-acct-v3.c

Purpose: compile probe for BSD/Linux accounting v3 structure fields. It exists to let the stress-ng build detect whether this platform exposes the API, type, constant, header, or library call needed by guarded stressor code.

Important APIs/types/functions: observed call/type/function symbols include `main` only with compile-time expressions; includes: `<sys/acct.h>`; macros: `_GNU_SOURCE`.

Control flow: `main` declares minimal arguments, invokes or references the target API/type, and returns the result or zero. Invalid descriptors, null-ish arguments, or dummy structures are acceptable because compile/link availability is the primary goal.

State and persistence behavior: any state is local to the probe process. The file does not intentionally create durable resources; when it opens or allocates anything, the scope is limited to proving the symbol and signature are usable.

Dependencies and integration points: this probe contributes one feature bit to stress-ng's generated configuration, enabling or disabling code paths that use `acct-v3`. Some probes also require external libraries such as libacl, libbsd, libc realtime/AIO support, or platform-specific headers.

Risks and test signals: successful compilation may not imply the call succeeds at runtime with dummy arguments, sufficient privileges, or all kernels. Failures indicate missing headers, declarations, libraries, constants, or incompatible signatures.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-acct-v3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-acct.c -->
# sources/test-tools/stress-ng/test/test-acct.c

Purpose: compile probe for the `acct()` process accounting system call. It exists to let the stress-ng build detect whether this platform exposes the API, type, constant, header, or library call needed by guarded stressor code.

Important APIs/types/functions: observed call/type/function symbols include `acct`; includes: `<unistd.h>`; macros: none.

Control flow: `main` declares minimal arguments, invokes or references the target API/type, and returns the result or zero. Invalid descriptors, null-ish arguments, or dummy structures are acceptable because compile/link availability is the primary goal.

State and persistence behavior: any state is local to the probe process. The file does not intentionally create durable resources; when it opens or allocates anything, the scope is limited to proving the symbol and signature are usable.

Dependencies and integration points: this probe contributes one feature bit to stress-ng's generated configuration, enabling or disabling code paths that use `acct`. Some probes also require external libraries such as libacl, libbsd, libc realtime/AIO support, or platform-specific headers.

Risks and test signals: successful compilation may not imply the call succeeds at runtime with dummy arguments, sufficient privileges, or all kernels. Failures indicate missing headers, declarations, libraries, constants, or incompatible signatures.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-acct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-acl-cmp.c -->
# sources/test-tools/stress-ng/test/test-acl-cmp.c

Purpose: compile probe for libacl `acl_cmp`. It exists to let the stress-ng build detect whether this platform exposes the API, type, constant, header, or library call needed by guarded stressor code.

Important APIs/types/functions: observed call/type/function symbols include `acl_init`, `acl_cmp`; includes: `<acl/libacl.h>`; macros: none.

Control flow: `main` declares minimal arguments, invokes or references the target API/type, and returns the result or zero. Invalid descriptors, null-ish arguments, or dummy structures are acceptable because compile/link availability is the primary goal.

State and persistence behavior: any state is local to the probe process. The file does not intentionally create durable resources; when it opens or allocates anything, the scope is limited to proving the symbol and signature are usable.

Dependencies and integration points: this probe contributes one feature bit to stress-ng's generated configuration, enabling or disabling code paths that use `acl-cmp`. Some probes also require external libraries such as libacl, libbsd, libc realtime/AIO support, or platform-specific headers.

Risks and test signals: successful compilation may not imply the call succeeds at runtime with dummy arguments, sufficient privileges, or all kernels. Failures indicate missing headers, declarations, libraries, constants, or incompatible signatures.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-acl-cmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-adjtime.c -->
# sources/test-tools/stress-ng/test/test-adjtime.c

Purpose: compile probe for the `adjtime()` clock adjustment call. It exists to let the stress-ng build detect whether this platform exposes the API, type, constant, header, or library call needed by guarded stressor code.

Important APIs/types/functions: observed call/type/function symbols include `memset`, `adjtime`; includes: `<string.h>`, `<sys/time.h>`; macros: none.

Control flow: `main` declares minimal arguments, invokes or references the target API/type, and returns the result or zero. Invalid descriptors, null-ish arguments, or dummy structures are acceptable because compile/link availability is the primary goal.

State and persistence behavior: any state is local to the probe process. The file does not intentionally create durable resources; when it opens or allocates anything, the scope is limited to proving the symbol and signature are usable.

Dependencies and integration points: this probe contributes one feature bit to stress-ng's generated configuration, enabling or disabling code paths that use `adjtime`. Some probes also require external libraries such as libacl, libbsd, libc realtime/AIO support, or platform-specific headers.

Risks and test signals: successful compilation may not imply the call succeeds at runtime with dummy arguments, sufficient privileges, or all kernels. Failures indicate missing headers, declarations, libraries, constants, or incompatible signatures.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-adjtime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-adjtimex.c -->
# sources/test-tools/stress-ng/test/test-adjtimex.c

Purpose: compile probe for the `adjtimex()` time tuning call and `struct timex`. It exists to let the stress-ng build detect whether this platform exposes the API, type, constant, header, or library call needed by guarded stressor code.

Important APIs/types/functions: observed call/type/function symbols include `adjtimex`; includes: `<sys/timex.h>`; macros: none.

Control flow: `main` declares minimal arguments, invokes or references the target API/type, and returns the result or zero. Invalid descriptors, null-ish arguments, or dummy structures are acceptable because compile/link availability is the primary goal.

State and persistence behavior: any state is local to the probe process. The file does not intentionally create durable resources; when it opens or allocates anything, the scope is limited to proving the symbol and signature are usable.

Dependencies and integration points: this probe contributes one feature bit to stress-ng's generated configuration, enabling or disabling code paths that use `adjtimex`. Some probes also require external libraries such as libacl, libbsd, libc realtime/AIO support, or platform-specific headers.

Risks and test signals: successful compilation may not imply the call succeeds at runtime with dummy arguments, sufficient privileges, or all kernels. Failures indicate missing headers, declarations, libraries, constants, or incompatible signatures.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-adjtimex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-aio-cancel.c -->
# sources/test-tools/stress-ng/test/test-aio-cancel.c

Purpose: compile probe for POSIX AIO `aio_cancel`. It exists to let the stress-ng build detect whether this platform exposes the API, type, constant, header, or library call needed by guarded stressor code.

Important APIs/types/functions: observed call/type/function symbols include `memset`, `aio_cancel`; includes: `<string.h>`, `<aio.h>`; macros: none.

Control flow: `main` declares minimal arguments, invokes or references the target API/type, and returns the result or zero. Invalid descriptors, null-ish arguments, or dummy structures are acceptable because compile/link availability is the primary goal.

State and persistence behavior: any state is local to the probe process. The file does not intentionally create durable resources; when it opens or allocates anything, the scope is limited to proving the symbol and signature are usable.

Dependencies and integration points: this probe contributes one feature bit to stress-ng's generated configuration, enabling or disabling code paths that use `aio-cancel`. Some probes also require external libraries such as libacl, libbsd, libc realtime/AIO support, or platform-specific headers.

Risks and test signals: successful compilation may not imply the call succeeds at runtime with dummy arguments, sufficient privileges, or all kernels. Failures indicate missing headers, declarations, libraries, constants, or incompatible signatures.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-aio-cancel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-aio-fsync.c -->
# sources/test-tools/stress-ng/test/test-aio-fsync.c

Purpose: compile probe for POSIX AIO `aio_fsync`. It exists to let the stress-ng build detect whether this platform exposes the API, type, constant, header, or library call needed by guarded stressor code.

Important APIs/types/functions: observed call/type/function symbols include `memset`, `aio_fsync`; includes: `<string.h>`, `<fcntl.h>`, `<aio.h>`; macros: none.

Control flow: `main` declares minimal arguments, invokes or references the target API/type, and returns the result or zero. Invalid descriptors, null-ish arguments, or dummy structures are acceptable because compile/link availability is the primary goal.

State and persistence behavior: any state is local to the probe process. The file does not intentionally create durable resources; when it opens or allocates anything, the scope is limited to proving the symbol and signature are usable.

Dependencies and integration points: this probe contributes one feature bit to stress-ng's generated configuration, enabling or disabling code paths that use `aio-fsync`. Some probes also require external libraries such as libacl, libbsd, libc realtime/AIO support, or platform-specific headers.

Risks and test signals: successful compilation may not imply the call succeeds at runtime with dummy arguments, sufficient privileges, or all kernels. Failures indicate missing headers, declarations, libraries, constants, or incompatible signatures.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-aio-fsync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-aio-read.c -->
# sources/test-tools/stress-ng/test/test-aio-read.c

Purpose: compile probe for POSIX AIO `aio_read`. It exists to let the stress-ng build detect whether this platform exposes the API, type, constant, header, or library call needed by guarded stressor code.

Important APIs/types/functions: observed call/type/function symbols include `memset`, `aio_read`; includes: `<string.h>`, `<aio.h>`; macros: none.

Control flow: `main` declares minimal arguments, invokes or references the target API/type, and returns the result or zero. Invalid descriptors, null-ish arguments, or dummy structures are acceptable because compile/link availability is the primary goal.

State and persistence behavior: any state is local to the probe process. The file does not intentionally create durable resources; when it opens or allocates anything, the scope is limited to proving the symbol and signature are usable.

Dependencies and integration points: this probe contributes one feature bit to stress-ng's generated configuration, enabling or disabling code paths that use `aio-read`. Some probes also require external libraries such as libacl, libbsd, libc realtime/AIO support, or platform-specific headers.

Risks and test signals: successful compilation may not imply the call succeeds at runtime with dummy arguments, sufficient privileges, or all kernels. Failures indicate missing headers, declarations, libraries, constants, or incompatible signatures.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-aio-read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-aio-write.c -->
# sources/test-tools/stress-ng/test/test-aio-write.c

Purpose: compile probe for POSIX AIO `aio_write`. It exists to let the stress-ng build detect whether this platform exposes the API, type, constant, header, or library call needed by guarded stressor code.

Important APIs/types/functions: observed call/type/function symbols include `memset`, `aio_write`; includes: `<string.h>`, `<aio.h>`; macros: none.

Control flow: `main` declares minimal arguments, invokes or references the target API/type, and returns the result or zero. Invalid descriptors, null-ish arguments, or dummy structures are acceptable because compile/link availability is the primary goal.

State and persistence behavior: any state is local to the probe process. The file does not intentionally create durable resources; when it opens or allocates anything, the scope is limited to proving the symbol and signature are usable.

Dependencies and integration points: this probe contributes one feature bit to stress-ng's generated configuration, enabling or disabling code paths that use `aio-write`. Some probes also require external libraries such as libacl, libbsd, libc realtime/AIO support, or platform-specific headers.

Risks and test signals: successful compilation may not imply the call succeeds at runtime with dummy arguments, sufficient privileges, or all kernels. Failures indicate missing headers, declarations, libraries, constants, or incompatible signatures.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-aio-write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-aligned-128.c -->
# sources/test-tools/stress-ng/test/test-aligned-128.c

Purpose: compile probe for alignment support `128`, covering either compiler alignment attributes or aligned allocation APIs required by stress-ng data buffers and vector-friendly structures.

Important APIs/types/functions: alignment declarations or allocation calls; observed symbols: `__attribute__`, `aligned`, `test_align128`; includes: `<stdint.h>`; macros: none.

Control flow: `main` declares or allocates an object with the requested alignment and returns after the compiler has type-checked the construct. Any free call is only cleanup for allocation probes.

State and persistence behavior: state is local stack or heap memory for the duration of the probe. No persistent resources are retained.

Dependencies and integration points: informs stress-ng whether it can request cacheline/page/large alignment in hot buffers, shared structures, or SIMD-oriented test data. Failed probes force less-specific allocation or declaration paths.

Risks and test signals: alignment syntax and maximum supported alignment vary by compiler, standard library, and target ABI. Compile/link success is the key signal; it does not guarantee every runtime allocation request will succeed under memory pressure.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-aligned-128.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-aligned-64.c -->
# sources/test-tools/stress-ng/test/test-aligned-64.c

Purpose: compile probe for alignment support `64`, covering either compiler alignment attributes or aligned allocation APIs required by stress-ng data buffers and vector-friendly structures.

Important APIs/types/functions: alignment declarations or allocation calls; observed symbols: `__attribute__`, `aligned`, `test_align64`; includes: `<stdint.h>`; macros: none.

Control flow: `main` declares or allocates an object with the requested alignment and returns after the compiler has type-checked the construct. Any free call is only cleanup for allocation probes.

State and persistence behavior: state is local stack or heap memory for the duration of the probe. No persistent resources are retained.

Dependencies and integration points: informs stress-ng whether it can request cacheline/page/large alignment in hot buffers, shared structures, or SIMD-oriented test data. Failed probes force less-specific allocation or declaration paths.

Risks and test signals: alignment syntax and maximum supported alignment vary by compiler, standard library, and target ABI. Compile/link success is the key signal; it does not guarantee every runtime allocation request will succeed under memory pressure.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-aligned-64.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-aligned-64K.c -->
# sources/test-tools/stress-ng/test/test-aligned-64K.c

Purpose: compile probe for alignment support `64K`, covering either compiler alignment attributes or aligned allocation APIs required by stress-ng data buffers and vector-friendly structures.

Important APIs/types/functions: alignment declarations or allocation calls; observed symbols: `__attribute__`, `aligned`, `test_align64K`; includes: `<stdint.h>`; macros: none.

Control flow: `main` declares or allocates an object with the requested alignment and returns after the compiler has type-checked the construct. Any free call is only cleanup for allocation probes.

State and persistence behavior: state is local stack or heap memory for the duration of the probe. No persistent resources are retained.

Dependencies and integration points: informs stress-ng whether it can request cacheline/page/large alignment in hot buffers, shared structures, or SIMD-oriented test data. Failed probes force less-specific allocation or declaration paths.

Risks and test signals: alignment syntax and maximum supported alignment vary by compiler, standard library, and target ABI. Compile/link success is the key signal; it does not guarantee every runtime allocation request will succeed under memory pressure.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-aligned-64K.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-aligned-alloc.c -->
# sources/test-tools/stress-ng/test/test-aligned-alloc.c

Purpose: compile probe for alignment support `alloc`, covering either compiler alignment attributes or aligned allocation APIs required by stress-ng data buffers and vector-friendly structures.

Important APIs/types/functions: alignment declarations or allocation calls; observed symbols: `aligned_alloc`, `free`; includes: `<stdlib.h>`; macros: `_GNU_SOURCE`.

Control flow: `main` declares or allocates an object with the requested alignment and returns after the compiler has type-checked the construct. Any free call is only cleanup for allocation probes.

State and persistence behavior: state is local stack or heap memory for the duration of the probe. No persistent resources are retained.

Dependencies and integration points: informs stress-ng whether it can request cacheline/page/large alignment in hot buffers, shared structures, or SIMD-oriented test data. Failed probes force less-specific allocation or declaration paths.

Risks and test signals: alignment syntax and maximum supported alignment vary by compiler, standard library, and target ABI. Compile/link success is the key signal; it does not guarantee every runtime allocation request will succeed under memory pressure.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-aligned-alloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-apparmor.c -->
# sources/test-tools/stress-ng/test/test-apparmor.c

Purpose: compile probe for AppArmor profile query interfaces. It exists to let the stress-ng build detect whether this platform exposes the API, type, constant, header, or library call needed by guarded stressor code.

Important APIs/types/functions: observed call/type/function symbols include `aa_is_enabled`, `aa_kernel_interface_new`, `aa_kernel_interface_load_policy`, `aa_kernel_interface_replace_policy`, `aa_kernel_interface_remove_policy`, `aa_kernel_interface_unref`; includes: `<unistd.h>`, `<sys/apparmor.h>`; macros: none.

Control flow: `main` declares minimal arguments, invokes or references the target API/type, and returns the result or zero. Invalid descriptors, null-ish arguments, or dummy structures are acceptable because compile/link availability is the primary goal.

State and persistence behavior: any state is local to the probe process. The file does not intentionally create durable resources; when it opens or allocates anything, the scope is limited to proving the symbol and signature are usable.

Dependencies and integration points: this probe contributes one feature bit to stress-ng's generated configuration, enabling or disabling code paths that use `apparmor`. Some probes also require external libraries such as libacl, libbsd, libc realtime/AIO support, or platform-specific headers.

Risks and test signals: successful compilation may not imply the call succeeds at runtime with dummy arguments, sufficient privileges, or all kernels. Failures indicate missing headers, declarations, libraries, constants, or incompatible signatures.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-apparmor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-arc4random.c -->
# sources/test-tools/stress-ng/test/test-arc4random.c

Purpose: compile probe for BSD `arc4random()`. It exists to let the stress-ng build detect whether this platform exposes the API, type, constant, header, or library call needed by guarded stressor code.

Important APIs/types/functions: observed call/type/function symbols include `arc4random`; includes: `<stdlib.h>`; macros: none.

Control flow: `main` declares minimal arguments, invokes or references the target API/type, and returns the result or zero. Invalid descriptors, null-ish arguments, or dummy structures are acceptable because compile/link availability is the primary goal.

State and persistence behavior: any state is local to the probe process. The file does not intentionally create durable resources; when it opens or allocates anything, the scope is limited to proving the symbol and signature are usable.

Dependencies and integration points: this probe contributes one feature bit to stress-ng's generated configuration, enabling or disabling code paths that use `arc4random`. Some probes also require external libraries such as libacl, libbsd, libc realtime/AIO support, or platform-specific headers.

Risks and test signals: successful compilation may not imply the call succeeds at runtime with dummy arguments, sufficient privileges, or all kernels. Failures indicate missing headers, declarations, libraries, constants, or incompatible signatures.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-arc4random.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-arch_prctl.c -->
# sources/test-tools/stress-ng/test/test-arch_prctl.c

Purpose: compile probe for Linux x86 `arch_prctl` syscall constants and call shape. It exists to let the stress-ng build detect whether this platform exposes the API, type, constant, header, or library call needed by guarded stressor code.

Important APIs/types/functions: observed call/type/function symbols include `arch_prctl`; includes: `<asm/prctl.h>`, `<sys/prctl.h>`; macros: none.

Control flow: `main` declares minimal arguments, invokes or references the target API/type, and returns the result or zero. Invalid descriptors, null-ish arguments, or dummy structures are acceptable because compile/link availability is the primary goal.

State and persistence behavior: any state is local to the probe process. The file does not intentionally create durable resources; when it opens or allocates anything, the scope is limited to proving the symbol and signature are usable.

Dependencies and integration points: this probe contributes one feature bit to stress-ng's generated configuration, enabling or disabling code paths that use `arch_prctl`. Some probes also require external libraries such as libacl, libbsd, libc realtime/AIO support, or platform-specific headers.

Risks and test signals: successful compilation may not imply the call succeeds at runtime with dummy arguments, sufficient privileges, or all kernels. Failures indicate missing headers, declarations, libraries, constants, or incompatible signatures.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-arch_prctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-alpha-draina.c -->
# sources/test-tools/stress-ng/test/test-asm-alpha-draina.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-alpha-draina`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `call_pal %0 #draina`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `alpha` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-alpha-draina.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-alpha-halt.c -->
# sources/test-tools/stress-ng/test/test-asm-alpha-halt.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-alpha-halt`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `call_pal %0 #halt`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `alpha` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-alpha-halt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-arm-dmb-sy.c -->
# sources/test-tools/stress-ng/test/test-asm-arm-dmb-sy.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-arm-dmb-sy`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `dmb sy;\n`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `arm` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-arm-dmb-sy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-arm-prfm.c -->
# sources/test-tools/stress-ng/test/test-asm-arm-prfm.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-arm-prfm`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `prfm PLDL1KEEP, [%0]\n`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `arm` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-arm-prfm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-arm-tlbi.c -->
# sources/test-tools/stress-ng/test/test-asm-arm-tlbi.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-arm-tlbi`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `tlbi vmalle1is`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `arm` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-arm-tlbi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-arm-yield.c -->
# sources/test-tools/stress-ng/test/test-asm-arm-yield.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-arm-yield`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `yield;\n`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `arm` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-arm-yield.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-hppa-diag.c -->
# sources/test-tools/stress-ng/test/test-asm-hppa-diag.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-hppa-diag`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `diag 0`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `hppa` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-hppa-diag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-hppa-rfi.c -->
# sources/test-tools/stress-ng/test/test-asm-hppa-rfi.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-hppa-rfi`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `rfi`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `hppa` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-hppa-rfi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-loong64-cpucfg.c -->
# sources/test-tools/stress-ng/test/test-asm-loong64-cpucfg.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-loong64-cpucfg`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `cpucfg %1, %0\n`; includes: `<stdint.h>`; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `loong64` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-loong64-cpucfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-loong64-dbar.c -->
# sources/test-tools/stress-ng/test/test-asm-loong64-dbar.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-loong64-dbar`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `dbar 0`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `loong64` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-loong64-dbar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-loong64-rdtime.c -->
# sources/test-tools/stress-ng/test/test-asm-loong64-rdtime.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-loong64-rdtime`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `rdtime.d %0, $zero\n\t`; includes: `<stdint.h>`; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `loong64` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-loong64-rdtime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-loong64-tlbrd.c -->
# sources/test-tools/stress-ng/test/test-asm-loong64-tlbrd.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-loong64-tlbrd`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `tlbrd`; includes: `<stdint.h>`; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `loong64` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-loong64-tlbrd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-loong64-tlbsrch.c -->
# sources/test-tools/stress-ng/test/test-asm-loong64-tlbsrch.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-loong64-tlbsrch`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `tlbsrch`; includes: `<stdint.h>`; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `loong64` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-loong64-tlbsrch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-m68k-eori-sr.c -->
# sources/test-tools/stress-ng/test/test-asm-m68k-eori-sr.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-m68k-eori-sr`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `eori.w #0001,%sr`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `m68k` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-m68k-eori-sr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-mb.c -->
# sources/test-tools/stress-ng/test/test-asm-mb.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-mb`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: inline assembly present in architecture-guarded branches; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `mb` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-mb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-mips-wait.c -->
# sources/test-tools/stress-ng/test/test-asm-mips-wait.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-mips-wait`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `wait`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `mips` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-mips-wait.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-nop.c -->
# sources/test-tools/stress-ng/test/test-asm-nop.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-nop`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `nop;`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `nop` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-nop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-nothing.c -->
# sources/test-tools/stress-ng/test/test-asm-nothing.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-nothing`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: inline assembly present in architecture-guarded branches; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `nothing` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-nothing.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-openrisc-msync.c -->
# sources/test-tools/stress-ng/test/test-asm-openrisc-msync.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-openrisc-msync`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `l.msync;\n`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `openrisc` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-openrisc-msync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-openrisc-nop.c -->
# sources/test-tools/stress-ng/test/test-asm-openrisc-nop.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-openrisc-nop`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `l.nop;\n`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `openrisc` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-openrisc-nop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-openrisc-psync.c -->
# sources/test-tools/stress-ng/test/test-asm-openrisc-psync.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-openrisc-psync`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `l.psync;\n`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `openrisc` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-openrisc-psync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-ppc-dcbst.c -->
# sources/test-tools/stress-ng/test/test-asm-ppc-dcbst.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-ppc-dcbst`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `dcbst %y0`; includes: `<stdint.h>`; helper symbols/functions observed: `dcbst`, `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `ppc` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-ppc-dcbst.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-ppc-dcbt.c -->
# sources/test-tools/stress-ng/test/test-asm-ppc-dcbt.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-ppc-dcbt`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `dcbt 0,%0`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `dcbt`, `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `ppc` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-ppc-dcbt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-ppc-dcbtst.c -->
# sources/test-tools/stress-ng/test/test-asm-ppc-dcbtst.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-ppc-dcbtst`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `dcbtst 0,%0`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `dcbtst`, `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `ppc` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-ppc-dcbtst.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-ppc-icbi.c -->
# sources/test-tools/stress-ng/test/test-asm-ppc-icbi.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-ppc-icbi`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `icbi %y0`; includes: `<stdint.h>`; helper symbols/functions observed: `icbi`, `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `ppc` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-ppc-icbi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-ppc64-darn.c -->
# sources/test-tools/stress-ng/test/test-asm-ppc64-darn.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-ppc64-darn`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `darn %0, 0\n`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `rand64`, `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `ppc64` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-ppc64-darn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-ppc64-dcbst.c -->
# sources/test-tools/stress-ng/test/test-asm-ppc64-dcbst.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-ppc64-dcbst`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `dcbst %y0`; includes: `<stdint.h>`; helper symbols/functions observed: `dcbst`, `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `ppc64` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-ppc64-dcbst.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-ppc64-dcbt.c -->
# sources/test-tools/stress-ng/test/test-asm-ppc64-dcbt.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-ppc64-dcbt`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `dcbt 0,%0`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `dcbt`, `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `ppc64` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-ppc64-dcbt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-ppc64-dcbtst.c -->
# sources/test-tools/stress-ng/test/test-asm-ppc64-dcbtst.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-ppc64-dcbtst`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `dcbtst 0,%0`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `dcbtst`, `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `ppc64` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-ppc64-dcbtst.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-ppc64-icbi.c -->
# sources/test-tools/stress-ng/test/test-asm-ppc64-icbi.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-ppc64-icbi`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `icbi %y0`; includes: `<stdint.h>`; helper symbols/functions observed: `icbi`, `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `ppc64` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-ppc64-icbi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-ppc64-msync.c -->
# sources/test-tools/stress-ng/test/test-asm-ppc64-msync.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-ppc64-msync`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `msync`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `ppc64` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-ppc64-msync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-ppc64-tlbie.c -->
# sources/test-tools/stress-ng/test/test-asm-ppc64-tlbie.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-ppc64-tlbie`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `tlbie %0, 0`; includes: `<stdint.h>`; helper symbols/functions observed: `tlbie`, `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `ppc64` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-ppc64-tlbie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-riscv-cbo_zero.c -->
# sources/test-tools/stress-ng/test/test-asm-riscv-cbo_zero.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-riscv-cbo_zero`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: inline assembly present in architecture-guarded branches; includes: `<sched.h>`, `<stdint.h>`, `<string.h>`, `<sys/syscall.h>`, `<unistd.h>`, `<asm/hwprobe.h>`; helper symbols/functions observed: `__bswap32`, `__builtin_bswap32`, `MK_CBO`, `CBO_INSN`, `volatile`, `cbo_zero`, `__attribute__`, `aligned`, `memset`, `sched_getaffinity`, `syscall`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `riscv` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-riscv-cbo_zero.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-riscv-cbom.c -->
# sources/test-tools/stress-ng/test/test-asm-riscv-cbom.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-riscv-cbom`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: inline assembly present in architecture-guarded branches; includes: `<stdint.h>`, `<string.h>`, `<sched.h>`, `<sys/syscall.h>`, `<unistd.h>`, `<asm/hwprobe.h>`; helper symbols/functions observed: `__bswap32`, `__builtin_bswap32`, `MK_CBO`, `CBO_INSN`, `volatile`, `cbo_flush`, `__attribute__`, `aligned`, `memset`, `sched_getaffinity`, `syscall`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `riscv` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-riscv-cbom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-riscv-fence.c -->
# sources/test-tools/stress-ng/test/test-asm-riscv-fence.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-riscv-fence`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `fence`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `riscv` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-riscv-fence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-riscv-fence_i.c -->
# sources/test-tools/stress-ng/test/test-asm-riscv-fence_i.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-riscv-fence_i`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `fence.i`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `riscv` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-riscv-fence_i.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-riscv-sfence-vma.c -->
# sources/test-tools/stress-ng/test/test-asm-riscv-sfence-vma.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-riscv-sfence-vma`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `sfence.vma`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `riscv` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-riscv-sfence-vma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-s390-ptlb.c -->
# sources/test-tools/stress-ng/test/test-asm-s390-ptlb.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-s390-ptlb`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `ptlb`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `s390` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-s390-ptlb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-sh4-rte.c -->
# sources/test-tools/stress-ng/test/test-asm-sh4-rte.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-sh4-rte`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `rte`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `sh4` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-sh4-rte.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-sh4-sleep.c -->
# sources/test-tools/stress-ng/test/test-asm-sh4-sleep.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-sh4-sleep`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `sleep`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `sh4` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-sh4-sleep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-sparc-membar.c -->
# sources/test-tools/stress-ng/test/test-asm-sparc-membar.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-sparc-membar`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `membar #StoreLoad`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `sparc` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-sparc-membar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-sparc-rdpr.c -->
# sources/test-tools/stress-ng/test/test-asm-sparc-rdpr.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-sparc-rdpr`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `rdpr %%ver, %0`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `sparc` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-sparc-rdpr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-sparc-tick.c -->
# sources/test-tools/stress-ng/test/test-asm-sparc-tick.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-sparc-tick`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `rd %%tick, %0`; includes: `<stdint.h>`; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `sparc` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-sparc-tick.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-cldemote.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-cldemote.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-cldemote`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `cldemote (%0)\n`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `cldemote`, `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-cldemote.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-clflush.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-clflush.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-clflush`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `clflush (%0)\n`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `clflush`, `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-clflush.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-clflushopt.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-clflushopt.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-clflushopt`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `clflushopt (%0)\n`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `clflushopt`, `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-clflushopt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-clts.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-clts.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-clts`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `clts`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-clts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-clwb.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-clwb.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-clwb`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `clwb (%0)\n`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `clwb`, `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-clwb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-hlt.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-hlt.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-hlt`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `hlt`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-hlt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-invd.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-invd.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-invd`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `invd`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-invd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-invlpg.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-invlpg.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-invlpg`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `invlpg (%0)`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`, `invlpg`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-invlpg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-lahf.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-lahf.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-lahf`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `lahf;\n`; includes: `<stdint.h>`; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-lahf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-lfence.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-lfence.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-lfence`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `lfence`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-lfence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-lgdt.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-lgdt.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-lgdt`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `lgdt (%0)`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`, `lgdt`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-lgdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-lldt.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-lldt.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-lldt`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `lldt %0`; includes: `<stdint.h>`; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-lldt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-lmsw.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-lmsw.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-lmsw`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `lmsw %0`; includes: `<stdint.h>`; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-lmsw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-mfence.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-mfence.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-mfence`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `mfence`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-mfence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-mov-cr0.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-mov-cr0.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-mov-cr0`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `mov %%cr0, %0`; includes: `<stdint.h>`; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-mov-cr0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-mov-dr0.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-mov-dr0.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-mov-dr0`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `mov %%dr0, %0`; includes: `<stdint.h>`; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-mov-dr0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-movdiri.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-movdiri.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-movdiri`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `movdiri %0, (%1)\n`; includes: `<inttypes.h>`; helper symbols/functions observed: `stress_ds_store64`, `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-movdiri.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-pause.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-pause.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-pause`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `pause;\n`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-pause.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-prefetchnta.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-prefetchnta.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-prefetchnta`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `prefetchnta (%0)\n`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `prefetchnta`, `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-prefetchnta.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-prefetcht0.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-prefetcht0.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-prefetcht0`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `prefetcht0 (%0)\n`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `prefetcht0`, `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-prefetcht0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-prefetcht1.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-prefetcht1.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-prefetcht1`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `prefetcht1 (%0)\n`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `prefetcht1`, `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-prefetcht1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-prefetcht2.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-prefetcht2.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-prefetcht2`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `prefetcht2 (%0)\n`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `prefetcht2`, `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-prefetcht2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-prefetchw.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-prefetchw.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-prefetchw`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `prefetchw (%0)\n`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `prefetchw`, `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-prefetchw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-prefetchwt1.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-prefetchwt1.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-prefetchwt1`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `prefetchwt1 (%0)\n`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `prefetchwt1`, `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-prefetchwt1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-rdmsr.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-rdmsr.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-rdmsr`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `rdmsr`; includes: `<stdint.h>`; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-rdmsr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-rdpmc.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-rdpmc.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-rdpmc`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `rdpmc`; includes: `<stdint.h>`; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-rdpmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-rdrand.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-rdrand.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-rdrand`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `1:;\n\
		     rdrand %0;\n\
		     jnc 1b;\n`; includes: `<stdint.h>`; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-rdrand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-rdseed.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-rdseed.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-rdseed`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `1:;\n\
		     rdseed %0;\n\
		     jnc 1b;\n`; includes: `<stdint.h>`; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-rdseed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-rdtsc.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-rdtsc.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-rdtsc`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `rdtsc`, `rdtsc`; includes: `<stdint.h>`; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-rdtsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-rdtscp.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-rdtscp.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-rdtscp`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `rdtscp`; includes: `<stdint.h>`; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-rdtscp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-rep-stosb.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-rep-stosb.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-rep-stosb`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `mov $0x00,%%al\n;`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `repzero`, `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-rep-stosb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-rep-stosd.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-rep-stosd.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-rep-stosd`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `mov $0xaaaaaaaa,%%eax\n;`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `repzero`, `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-rep-stosd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-rep-stosq.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-rep-stosq.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-rep-stosq`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `mov $0xaaaaaaaaaaaaaaaa,%%rax\n;`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `repzero`, `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-rep-stosq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-rep-stosw.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-rep-stosw.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-rep-stosw`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `mov $0xaaaa,%%ax\n;`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `repzero`, `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-rep-stosw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-serialize.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-serialize.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-serialize`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `serialize`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-serialize.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-sfence.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-sfence.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-sfence`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `sfence`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-sfence.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-tpause.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-tpause.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-tpause`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `tpause %%ecx\n`; includes: `<stdint.h>`; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-tpause.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-wbinvd.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-wbinvd.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-wbinvd`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `wbinvd`; includes: no external include beyond compiler defaults; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-wbinvd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-wrmsr.c -->
# sources/test-tools/stress-ng/test/test-asm-x86-wrmsr.c

Purpose: compile probe for an architecture-specific inline assembly instruction or instruction family named `asm-x86-wrmsr`. It confirms the compiler, assembler, target architecture macros, and constraints accept the instruction used by stress-ng fast paths or low-level stressors.

Important APIs/types/functions: inline assembly via `__asm__ __volatile__`; assembly snippets: `wrmsr`; includes: `<stdint.h>`; helper symbols/functions observed: `__volatile__`.

Control flow: `main` is guarded by architecture preprocessor checks, declares any required operands or scratch storage, emits the instruction, and returns a value or zero. Unsupported architectures generally hit `#error` so the build records the feature as unavailable.

State and persistence behavior: only CPU registers or stack temporaries are touched. There is no persistent state; privileged or trapping instructions are represented as compile probes, not production execution tests.

Dependencies and integration points: feeds stress-ng's build-time capability matrix for `x86` assembly support. Successful compilation enables guarded code paths in core architecture helpers or stressors; failure keeps portable fallbacks or unimplemented paths.

Risks and test signals: assembler syntax, register constraints, privilege level, and target flags can differ by compiler/binutils version. A successful compile means the syntax is accepted, not necessarily that executing the instruction is safe on every CPU at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-asm-x86-wrmsr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_add_fetch.c -->
# sources/test-tools/stress-ng/test/test-atomic_add_fetch.c

Purpose: compile probe for GCC/Clang `__atomic` builtin support, specifically `add_fetch` semantics as used by stress-ng portability shims.

Important APIs/types/functions: compiler atomic builtin calls; observed helper/function symbols: `__atomic_add_fetch`; includes: no external include beyond compiler defaults; macros: none.

Control flow: `main` declares one or more scalar variables, invokes the target `__atomic_*` builtin with a memory-order argument, and returns zero. The program is intentionally minimal because link/compile success is the feature signal.

State and persistence behavior: state is limited to local automatic variables modified or read atomically during process execution. No persistent state is created.

Dependencies and integration points: used by the stress-ng build system to decide whether native compiler atomics can back synchronization and low-level helper macros. Failure implies fallback or unavailable guarded code.

Risks and test signals: some targets support only certain widths or require libatomic at link time; double-width probes expose that risk. The expected signal is successful compilation/linking, not a correctness stress test under concurrency.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_add_fetch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_and_fetch.c -->
# sources/test-tools/stress-ng/test/test-atomic_and_fetch.c

Purpose: compile probe for GCC/Clang `__atomic` builtin support, specifically `and_fetch` semantics as used by stress-ng portability shims.

Important APIs/types/functions: compiler atomic builtin calls; observed helper/function symbols: `__atomic_and_fetch`; includes: no external include beyond compiler defaults; macros: none.

Control flow: `main` declares one or more scalar variables, invokes the target `__atomic_*` builtin with a memory-order argument, and returns zero. The program is intentionally minimal because link/compile success is the feature signal.

State and persistence behavior: state is limited to local automatic variables modified or read atomically during process execution. No persistent state is created.

Dependencies and integration points: used by the stress-ng build system to decide whether native compiler atomics can back synchronization and low-level helper macros. Failure implies fallback or unavailable guarded code.

Risks and test signals: some targets support only certain widths or require libatomic at link time; double-width probes expose that risk. The expected signal is successful compilation/linking, not a correctness stress test under concurrency.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_and_fetch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_clear.c -->
# sources/test-tools/stress-ng/test/test-atomic_clear.c

Purpose: compile probe for GCC/Clang `__atomic` builtin support, specifically `clear` semantics as used by stress-ng portability shims.

Important APIs/types/functions: compiler atomic builtin calls; observed helper/function symbols: `__atomic_clear`; includes: no external include beyond compiler defaults; macros: none.

Control flow: `main` declares one or more scalar variables, invokes the target `__atomic_*` builtin with a memory-order argument, and returns zero. The program is intentionally minimal because link/compile success is the feature signal.

State and persistence behavior: state is limited to local automatic variables modified or read atomically during process execution. No persistent state is created.

Dependencies and integration points: used by the stress-ng build system to decide whether native compiler atomics can back synchronization and low-level helper macros. Failure implies fallback or unavailable guarded code.

Risks and test signals: some targets support only certain widths or require libatomic at link time; double-width probes expose that risk. The expected signal is successful compilation/linking, not a correctness stress test under concurrency.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_clear.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_compare_exchange.c -->
# sources/test-tools/stress-ng/test/test-atomic_compare_exchange.c

Purpose: compile probe for GCC/Clang `__atomic` builtin support, specifically `compare_exchange` semantics as used by stress-ng portability shims.

Important APIs/types/functions: compiler atomic builtin calls; observed helper/function symbols: `__atomic_compare_exchange`; includes: no external include beyond compiler defaults; macros: none.

Control flow: `main` declares one or more scalar variables, invokes the target `__atomic_*` builtin with a memory-order argument, and returns zero. The program is intentionally minimal because link/compile success is the feature signal.

State and persistence behavior: state is limited to local automatic variables modified or read atomically during process execution. No persistent state is created.

Dependencies and integration points: used by the stress-ng build system to decide whether native compiler atomics can back synchronization and low-level helper macros. Failure implies fallback or unavailable guarded code.

Risks and test signals: some targets support only certain widths or require libatomic at link time; double-width probes expose that risk. The expected signal is successful compilation/linking, not a correctness stress test under concurrency.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_compare_exchange.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_fetch_add.c -->
# sources/test-tools/stress-ng/test/test-atomic_fetch_add.c

Purpose: compile probe for GCC/Clang `__atomic` builtin support, specifically `fetch_add` semantics as used by stress-ng portability shims.

Important APIs/types/functions: compiler atomic builtin calls; observed helper/function symbols: `__atomic_fetch_add`; includes: no external include beyond compiler defaults; macros: none.

Control flow: `main` declares one or more scalar variables, invokes the target `__atomic_*` builtin with a memory-order argument, and returns zero. The program is intentionally minimal because link/compile success is the feature signal.

State and persistence behavior: state is limited to local automatic variables modified or read atomically during process execution. No persistent state is created.

Dependencies and integration points: used by the stress-ng build system to decide whether native compiler atomics can back synchronization and low-level helper macros. Failure implies fallback or unavailable guarded code.

Risks and test signals: some targets support only certain widths or require libatomic at link time; double-width probes expose that risk. The expected signal is successful compilation/linking, not a correctness stress test under concurrency.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_fetch_add.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_fetch_add_2.c -->
# sources/test-tools/stress-ng/test/test-atomic_fetch_add_2.c

Purpose: compile probe for GCC/Clang `__atomic` builtin support, specifically `fetch_add_2` semantics as used by stress-ng portability shims.

Important APIs/types/functions: compiler atomic builtin calls; observed helper/function symbols: `__atomic_fetch_add_2`; includes: `<stdint.h>`; macros: none.

Control flow: `main` declares one or more scalar variables, invokes the target `__atomic_*` builtin with a memory-order argument, and returns zero. The program is intentionally minimal because link/compile success is the feature signal.

State and persistence behavior: state is limited to local automatic variables modified or read atomically during process execution. No persistent state is created.

Dependencies and integration points: used by the stress-ng build system to decide whether native compiler atomics can back synchronization and low-level helper macros. Failure implies fallback or unavailable guarded code.

Risks and test signals: some targets support only certain widths or require libatomic at link time; double-width probes expose that risk. The expected signal is successful compilation/linking, not a correctness stress test under concurrency.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_fetch_add_2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_fetch_add_4.c -->
# sources/test-tools/stress-ng/test/test-atomic_fetch_add_4.c

Purpose: compile probe for GCC/Clang `__atomic` builtin support, specifically `fetch_add_4` semantics as used by stress-ng portability shims.

Important APIs/types/functions: compiler atomic builtin calls; observed helper/function symbols: `__atomic_fetch_add_4`; includes: `<stdint.h>`; macros: none.

Control flow: `main` declares one or more scalar variables, invokes the target `__atomic_*` builtin with a memory-order argument, and returns zero. The program is intentionally minimal because link/compile success is the feature signal.

State and persistence behavior: state is limited to local automatic variables modified or read atomically during process execution. No persistent state is created.

Dependencies and integration points: used by the stress-ng build system to decide whether native compiler atomics can back synchronization and low-level helper macros. Failure implies fallback or unavailable guarded code.

Risks and test signals: some targets support only certain widths or require libatomic at link time; double-width probes expose that risk. The expected signal is successful compilation/linking, not a correctness stress test under concurrency.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_fetch_add_4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_fetch_add_8.c -->
# sources/test-tools/stress-ng/test/test-atomic_fetch_add_8.c

Purpose: compile probe for GCC/Clang `__atomic` builtin support, specifically `fetch_add_8` semantics as used by stress-ng portability shims.

Important APIs/types/functions: compiler atomic builtin calls; observed helper/function symbols: `__atomic_fetch_add_8`; includes: `<stdint.h>`; macros: none.

Control flow: `main` declares one or more scalar variables, invokes the target `__atomic_*` builtin with a memory-order argument, and returns zero. The program is intentionally minimal because link/compile success is the feature signal.

State and persistence behavior: state is limited to local automatic variables modified or read atomically during process execution. No persistent state is created.

Dependencies and integration points: used by the stress-ng build system to decide whether native compiler atomics can back synchronization and low-level helper macros. Failure implies fallback or unavailable guarded code.

Risks and test signals: some targets support only certain widths or require libatomic at link time; double-width probes expose that risk. The expected signal is successful compilation/linking, not a correctness stress test under concurrency.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_fetch_add_8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_fetch_and.c -->
# sources/test-tools/stress-ng/test/test-atomic_fetch_and.c

Purpose: compile probe for GCC/Clang `__atomic` builtin support, specifically `fetch_and` semantics as used by stress-ng portability shims.

Important APIs/types/functions: compiler atomic builtin calls; observed helper/function symbols: `__atomic_fetch_and`; includes: no external include beyond compiler defaults; macros: none.

Control flow: `main` declares one or more scalar variables, invokes the target `__atomic_*` builtin with a memory-order argument, and returns zero. The program is intentionally minimal because link/compile success is the feature signal.

State and persistence behavior: state is limited to local automatic variables modified or read atomically during process execution. No persistent state is created.

Dependencies and integration points: used by the stress-ng build system to decide whether native compiler atomics can back synchronization and low-level helper macros. Failure implies fallback or unavailable guarded code.

Risks and test signals: some targets support only certain widths or require libatomic at link time; double-width probes expose that risk. The expected signal is successful compilation/linking, not a correctness stress test under concurrency.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_fetch_and.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_fetch_nand.c -->
# sources/test-tools/stress-ng/test/test-atomic_fetch_nand.c

Purpose: compile probe for GCC/Clang `__atomic` builtin support, specifically `fetch_nand` semantics as used by stress-ng portability shims.

Important APIs/types/functions: compiler atomic builtin calls; observed helper/function symbols: `__atomic_fetch_nand`; includes: no external include beyond compiler defaults; macros: none.

Control flow: `main` declares one or more scalar variables, invokes the target `__atomic_*` builtin with a memory-order argument, and returns zero. The program is intentionally minimal because link/compile success is the feature signal.

State and persistence behavior: state is limited to local automatic variables modified or read atomically during process execution. No persistent state is created.

Dependencies and integration points: used by the stress-ng build system to decide whether native compiler atomics can back synchronization and low-level helper macros. Failure implies fallback or unavailable guarded code.

Risks and test signals: some targets support only certain widths or require libatomic at link time; double-width probes expose that risk. The expected signal is successful compilation/linking, not a correctness stress test under concurrency.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_fetch_nand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_fetch_or.c -->
# sources/test-tools/stress-ng/test/test-atomic_fetch_or.c

Purpose: compile probe for GCC/Clang `__atomic` builtin support, specifically `fetch_or` semantics as used by stress-ng portability shims.

Important APIs/types/functions: compiler atomic builtin calls; observed helper/function symbols: `__atomic_fetch_or`; includes: no external include beyond compiler defaults; macros: none.

Control flow: `main` declares one or more scalar variables, invokes the target `__atomic_*` builtin with a memory-order argument, and returns zero. The program is intentionally minimal because link/compile success is the feature signal.

State and persistence behavior: state is limited to local automatic variables modified or read atomically during process execution. No persistent state is created.

Dependencies and integration points: used by the stress-ng build system to decide whether native compiler atomics can back synchronization and low-level helper macros. Failure implies fallback or unavailable guarded code.

Risks and test signals: some targets support only certain widths or require libatomic at link time; double-width probes expose that risk. The expected signal is successful compilation/linking, not a correctness stress test under concurrency.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_fetch_or.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_fetch_sub.c -->
# sources/test-tools/stress-ng/test/test-atomic_fetch_sub.c

Purpose: compile probe for GCC/Clang `__atomic` builtin support, specifically `fetch_sub` semantics as used by stress-ng portability shims.

Important APIs/types/functions: compiler atomic builtin calls; observed helper/function symbols: `__atomic_fetch_sub`; includes: no external include beyond compiler defaults; macros: none.

Control flow: `main` declares one or more scalar variables, invokes the target `__atomic_*` builtin with a memory-order argument, and returns zero. The program is intentionally minimal because link/compile success is the feature signal.

State and persistence behavior: state is limited to local automatic variables modified or read atomically during process execution. No persistent state is created.

Dependencies and integration points: used by the stress-ng build system to decide whether native compiler atomics can back synchronization and low-level helper macros. Failure implies fallback or unavailable guarded code.

Risks and test signals: some targets support only certain widths or require libatomic at link time; double-width probes expose that risk. The expected signal is successful compilation/linking, not a correctness stress test under concurrency.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_fetch_sub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_fetch_xor.c -->
# sources/test-tools/stress-ng/test/test-atomic_fetch_xor.c

Purpose: compile probe for GCC/Clang `__atomic` builtin support, specifically `fetch_xor` semantics as used by stress-ng portability shims.

Important APIs/types/functions: compiler atomic builtin calls; observed helper/function symbols: `__atomic_fetch_xor`; includes: no external include beyond compiler defaults; macros: none.

Control flow: `main` declares one or more scalar variables, invokes the target `__atomic_*` builtin with a memory-order argument, and returns zero. The program is intentionally minimal because link/compile success is the feature signal.

State and persistence behavior: state is limited to local automatic variables modified or read atomically during process execution. No persistent state is created.

Dependencies and integration points: used by the stress-ng build system to decide whether native compiler atomics can back synchronization and low-level helper macros. Failure implies fallback or unavailable guarded code.

Risks and test signals: some targets support only certain widths or require libatomic at link time; double-width probes expose that risk. The expected signal is successful compilation/linking, not a correctness stress test under concurrency.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_fetch_xor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_load.c -->
# sources/test-tools/stress-ng/test/test-atomic_load.c

Purpose: compile probe for GCC/Clang `__atomic` builtin support, specifically `load` semantics as used by stress-ng portability shims.

Important APIs/types/functions: compiler atomic builtin calls; observed helper/function symbols: `__atomic_load`; includes: no external include beyond compiler defaults; macros: none.

Control flow: `main` declares one or more scalar variables, invokes the target `__atomic_*` builtin with a memory-order argument, and returns zero. The program is intentionally minimal because link/compile success is the feature signal.

State and persistence behavior: state is limited to local automatic variables modified or read atomically during process execution. No persistent state is created.

Dependencies and integration points: used by the stress-ng build system to decide whether native compiler atomics can back synchronization and low-level helper macros. Failure implies fallback or unavailable guarded code.

Risks and test signals: some targets support only certain widths or require libatomic at link time; double-width probes expose that risk. The expected signal is successful compilation/linking, not a correctness stress test under concurrency.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_load.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_load_double.c -->
# sources/test-tools/stress-ng/test/test-atomic_load_double.c

Purpose: compile probe for GCC/Clang `__atomic` builtin support, specifically `load_double` semantics as used by stress-ng portability shims.

Important APIs/types/functions: compiler atomic builtin calls; observed helper/function symbols: `__atomic_load`; includes: no external include beyond compiler defaults; macros: none.

Control flow: `main` declares one or more scalar variables, invokes the target `__atomic_*` builtin with a memory-order argument, and returns zero. The program is intentionally minimal because link/compile success is the feature signal.

State and persistence behavior: state is limited to local automatic variables modified or read atomically during process execution. No persistent state is created.

Dependencies and integration points: used by the stress-ng build system to decide whether native compiler atomics can back synchronization and low-level helper macros. Failure implies fallback or unavailable guarded code.

Risks and test signals: some targets support only certain widths or require libatomic at link time; double-width probes expose that risk. The expected signal is successful compilation/linking, not a correctness stress test under concurrency.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_load_double.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_nand_fetch.c -->
# sources/test-tools/stress-ng/test/test-atomic_nand_fetch.c

Purpose: compile probe for GCC/Clang `__atomic` builtin support, specifically `nand_fetch` semantics as used by stress-ng portability shims.

Important APIs/types/functions: compiler atomic builtin calls; observed helper/function symbols: `__atomic_nand_fetch`; includes: no external include beyond compiler defaults; macros: none.

Control flow: `main` declares one or more scalar variables, invokes the target `__atomic_*` builtin with a memory-order argument, and returns zero. The program is intentionally minimal because link/compile success is the feature signal.

State and persistence behavior: state is limited to local automatic variables modified or read atomically during process execution. No persistent state is created.

Dependencies and integration points: used by the stress-ng build system to decide whether native compiler atomics can back synchronization and low-level helper macros. Failure implies fallback or unavailable guarded code.

Risks and test signals: some targets support only certain widths or require libatomic at link time; double-width probes expose that risk. The expected signal is successful compilation/linking, not a correctness stress test under concurrency.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_nand_fetch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_or_fetch.c -->
# sources/test-tools/stress-ng/test/test-atomic_or_fetch.c

Purpose: compile probe for GCC/Clang `__atomic` builtin support, specifically `or_fetch` semantics as used by stress-ng portability shims.

Important APIs/types/functions: compiler atomic builtin calls; observed helper/function symbols: `__atomic_or_fetch`; includes: no external include beyond compiler defaults; macros: none.

Control flow: `main` declares one or more scalar variables, invokes the target `__atomic_*` builtin with a memory-order argument, and returns zero. The program is intentionally minimal because link/compile success is the feature signal.

State and persistence behavior: state is limited to local automatic variables modified or read atomically during process execution. No persistent state is created.

Dependencies and integration points: used by the stress-ng build system to decide whether native compiler atomics can back synchronization and low-level helper macros. Failure implies fallback or unavailable guarded code.

Risks and test signals: some targets support only certain widths or require libatomic at link time; double-width probes expose that risk. The expected signal is successful compilation/linking, not a correctness stress test under concurrency.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_or_fetch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_store.c -->
# sources/test-tools/stress-ng/test/test-atomic_store.c

Purpose: compile probe for GCC/Clang `__atomic` builtin support, specifically `store` semantics as used by stress-ng portability shims.

Important APIs/types/functions: compiler atomic builtin calls; observed helper/function symbols: `__atomic_store`; includes: no external include beyond compiler defaults; macros: none.

Control flow: `main` declares one or more scalar variables, invokes the target `__atomic_*` builtin with a memory-order argument, and returns zero. The program is intentionally minimal because link/compile success is the feature signal.

State and persistence behavior: state is limited to local automatic variables modified or read atomically during process execution. No persistent state is created.

Dependencies and integration points: used by the stress-ng build system to decide whether native compiler atomics can back synchronization and low-level helper macros. Failure implies fallback or unavailable guarded code.

Risks and test signals: some targets support only certain widths or require libatomic at link time; double-width probes expose that risk. The expected signal is successful compilation/linking, not a correctness stress test under concurrency.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_store.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_store_double.c -->
# sources/test-tools/stress-ng/test/test-atomic_store_double.c

Purpose: compile probe for GCC/Clang `__atomic` builtin support, specifically `store_double` semantics as used by stress-ng portability shims.

Important APIs/types/functions: compiler atomic builtin calls; observed helper/function symbols: `__atomic_store`; includes: no external include beyond compiler defaults; macros: none.

Control flow: `main` declares one or more scalar variables, invokes the target `__atomic_*` builtin with a memory-order argument, and returns zero. The program is intentionally minimal because link/compile success is the feature signal.

State and persistence behavior: state is limited to local automatic variables modified or read atomically during process execution. No persistent state is created.

Dependencies and integration points: used by the stress-ng build system to decide whether native compiler atomics can back synchronization and low-level helper macros. Failure implies fallback or unavailable guarded code.

Risks and test signals: some targets support only certain widths or require libatomic at link time; double-width probes expose that risk. The expected signal is successful compilation/linking, not a correctness stress test under concurrency.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_store_double.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_sub_fetch.c -->
# sources/test-tools/stress-ng/test/test-atomic_sub_fetch.c

Purpose: compile probe for GCC/Clang `__atomic` builtin support, specifically `sub_fetch` semantics as used by stress-ng portability shims.

Important APIs/types/functions: compiler atomic builtin calls; observed helper/function symbols: `__atomic_sub_fetch`; includes: no external include beyond compiler defaults; macros: none.

Control flow: `main` declares one or more scalar variables, invokes the target `__atomic_*` builtin with a memory-order argument, and returns zero. The program is intentionally minimal because link/compile success is the feature signal.

State and persistence behavior: state is limited to local automatic variables modified or read atomically during process execution. No persistent state is created.

Dependencies and integration points: used by the stress-ng build system to decide whether native compiler atomics can back synchronization and low-level helper macros. Failure implies fallback or unavailable guarded code.

Risks and test signals: some targets support only certain widths or require libatomic at link time; double-width probes expose that risk. The expected signal is successful compilation/linking, not a correctness stress test under concurrency.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_sub_fetch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_test_and_set.c -->
# sources/test-tools/stress-ng/test/test-atomic_test_and_set.c

Purpose: compile probe for GCC/Clang `__atomic` builtin support, specifically `test_and_set` semantics as used by stress-ng portability shims.

Important APIs/types/functions: compiler atomic builtin calls; observed helper/function symbols: `__atomic_test_and_set`; includes: `<stdbool.h>`; macros: none.

Control flow: `main` declares one or more scalar variables, invokes the target `__atomic_*` builtin with a memory-order argument, and returns zero. The program is intentionally minimal because link/compile success is the feature signal.

State and persistence behavior: state is limited to local automatic variables modified or read atomically during process execution. No persistent state is created.

Dependencies and integration points: used by the stress-ng build system to decide whether native compiler atomics can back synchronization and low-level helper macros. Failure implies fallback or unavailable guarded code.

Risks and test signals: some targets support only certain widths or require libatomic at link time; double-width probes expose that risk. The expected signal is successful compilation/linking, not a correctness stress test under concurrency.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_test_and_set.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_xor_fetch.c -->
# sources/test-tools/stress-ng/test/test-atomic_xor_fetch.c

Purpose: compile probe for GCC/Clang `__atomic` builtin support, specifically `xor_fetch` semantics as used by stress-ng portability shims.

Important APIs/types/functions: compiler atomic builtin calls; observed helper/function symbols: `__atomic_xor_fetch`; includes: no external include beyond compiler defaults; macros: none.

Control flow: `main` declares one or more scalar variables, invokes the target `__atomic_*` builtin with a memory-order argument, and returns zero. The program is intentionally minimal because link/compile success is the feature signal.

State and persistence behavior: state is limited to local automatic variables modified or read atomically during process execution. No persistent state is created.

Dependencies and integration points: used by the stress-ng build system to decide whether native compiler atomics can back synchronization and low-level helper macros. Failure implies fallback or unavailable guarded code.

Risks and test signals: some targets support only certain widths or require libatomic at link time; double-width probes expose that risk. The expected signal is successful compilation/linking, not a correctness stress test under concurrency.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-atomic_xor_fetch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-attr-always_inline.c -->
# sources/test-tools/stress-ng/test/test-attr-always_inline.c

Purpose: compile probe for compiler attribute support for `always_inline`, ensuring stress-ng can annotate functions, types, or objects with the corresponding optimization/diagnostic contract.

Important APIs/types/functions: `__attribute__` syntax or related compiler annotation forms; observed symbols: `__attribute__`, `inline_func`; includes: no external include beyond compiler defaults; macros: `ALWAYS_INLINE`.

Control flow: the file declares an annotated function/type/object and calls or references it from `main` when needed. Runtime behavior is incidental; the compile result is the detection signal.

State and persistence behavior: no persistent state. Any locals or static examples exist only to force the compiler to parse and type-check the attribute.

Dependencies and integration points: feeds stress-ng portability macros such as inline, noinline, noreturn, pure/const, packed, unused, weak, and returns-nonnull style annotations. Successful probes allow the main code to use stronger compiler hints without breaking other toolchains.

Risks and test signals: compilers may accept an attribute but ignore it, warn under different flags, or require placement on a specific declaration form. The meaningful signal is clean compilation with the configured warning policy.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-attr-always_inline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-attr-const.c -->
# sources/test-tools/stress-ng/test/test-attr-const.c

Purpose: compile probe for compiler attribute support for `const`, ensuring stress-ng can annotate functions, types, or objects with the corresponding optimization/diagnostic contract.

Important APIs/types/functions: `__attribute__` syntax or related compiler annotation forms; observed symbols: `__attribute__`, `const_func`; includes: no external include beyond compiler defaults; macros: `CONST`.

Control flow: the file declares an annotated function/type/object and calls or references it from `main` when needed. Runtime behavior is incidental; the compile result is the detection signal.

State and persistence behavior: no persistent state. Any locals or static examples exist only to force the compiler to parse and type-check the attribute.

Dependencies and integration points: feeds stress-ng portability macros such as inline, noinline, noreturn, pure/const, packed, unused, weak, and returns-nonnull style annotations. Successful probes allow the main code to use stronger compiler hints without breaking other toolchains.

Risks and test signals: compilers may accept an attribute but ignore it, warn under different flags, or require placement on a specific declaration form. The meaningful signal is clean compilation with the configured warning policy.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-attr-const.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-attr-fast-math.c -->
# sources/test-tools/stress-ng/test/test-attr-fast-math.c

Purpose: compile probe for compiler attribute support for `fast-math`, ensuring stress-ng can annotate functions, types, or objects with the corresponding optimization/diagnostic contract.

Important APIs/types/functions: `__attribute__` syntax or related compiler annotation forms; observed symbols: `__attribute__`, `optimize`, `do_math`; includes: no external include beyond compiler defaults; macros: `OPTIMIZE_FAST_MATH`.

Control flow: the file declares an annotated function/type/object and calls or references it from `main` when needed. Runtime behavior is incidental; the compile result is the detection signal.

State and persistence behavior: no persistent state. Any locals or static examples exist only to force the compiler to parse and type-check the attribute.

Dependencies and integration points: feeds stress-ng portability macros such as inline, noinline, noreturn, pure/const, packed, unused, weak, and returns-nonnull style annotations. Successful probes allow the main code to use stronger compiler hints without breaking other toolchains.

Risks and test signals: compilers may accept an attribute but ignore it, warn under different flags, or require placement on a specific declaration form. The meaningful signal is clean compilation with the configured warning policy.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-attr-fast-math.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-attr-noinline.c -->
# sources/test-tools/stress-ng/test/test-attr-noinline.c

Purpose: compile probe for compiler attribute support for `noinline`, ensuring stress-ng can annotate functions, types, or objects with the corresponding optimization/diagnostic contract.

Important APIs/types/functions: `__attribute__` syntax or related compiler annotation forms; observed symbols: `__attribute__`, `noinline_func`; includes: no external include beyond compiler defaults; macros: `NOINLINE`.

Control flow: the file declares an annotated function/type/object and calls or references it from `main` when needed. Runtime behavior is incidental; the compile result is the detection signal.

State and persistence behavior: no persistent state. Any locals or static examples exist only to force the compiler to parse and type-check the attribute.

Dependencies and integration points: feeds stress-ng portability macros such as inline, noinline, noreturn, pure/const, packed, unused, weak, and returns-nonnull style annotations. Successful probes allow the main code to use stronger compiler hints without breaking other toolchains.

Risks and test signals: compilers may accept an attribute but ignore it, warn under different flags, or require placement on a specific declaration form. The meaningful signal is clean compilation with the configured warning policy.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-attr-noinline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-attr-noreturn.c -->
# sources/test-tools/stress-ng/test/test-attr-noreturn.c

Purpose: compile probe for compiler attribute support for `noreturn`, ensuring stress-ng can annotate functions, types, or objects with the corresponding optimization/diagnostic contract.

Important APIs/types/functions: `__attribute__` syntax or related compiler annotation forms; observed symbols: `__attribute__`, `noreturn_func`, `_exit`; includes: `<unistd.h>`, `<stdlib.h>`; macros: `NORETURN`.

Control flow: the file declares an annotated function/type/object and calls or references it from `main` when needed. Runtime behavior is incidental; the compile result is the detection signal.

State and persistence behavior: no persistent state. Any locals or static examples exist only to force the compiler to parse and type-check the attribute.

Dependencies and integration points: feeds stress-ng portability macros such as inline, noinline, noreturn, pure/const, packed, unused, weak, and returns-nonnull style annotations. Successful probes allow the main code to use stronger compiler hints without breaking other toolchains.

Risks and test signals: compilers may accept an attribute but ignore it, warn under different flags, or require placement on a specific declaration form. The meaningful signal is clean compilation with the configured warning policy.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-attr-noreturn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-attr-packed.c -->
# sources/test-tools/stress-ng/test/test-attr-packed.c

Purpose: compile probe for compiler attribute support for `packed`, ensuring stress-ng can annotate functions, types, or objects with the corresponding optimization/diagnostic contract.

Important APIs/types/functions: `__attribute__` syntax or related compiler annotation forms; observed symbols: `__attribute__`; includes: no external include beyond compiler defaults; macros: `PACKED`.

Control flow: the file declares an annotated function/type/object and calls or references it from `main` when needed. Runtime behavior is incidental; the compile result is the detection signal.

State and persistence behavior: no persistent state. Any locals or static examples exist only to force the compiler to parse and type-check the attribute.

Dependencies and integration points: feeds stress-ng portability macros such as inline, noinline, noreturn, pure/const, packed, unused, weak, and returns-nonnull style annotations. Successful probes allow the main code to use stronger compiler hints without breaking other toolchains.

Risks and test signals: compilers may accept an attribute but ignore it, warn under different flags, or require placement on a specific declaration form. The meaningful signal is clean compilation with the configured warning policy.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-attr-packed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-attr-pure.c -->
# sources/test-tools/stress-ng/test/test-attr-pure.c

Purpose: compile probe for compiler attribute support for `pure`, ensuring stress-ng can annotate functions, types, or objects with the corresponding optimization/diagnostic contract.

Important APIs/types/functions: `__attribute__` syntax or related compiler annotation forms; observed symbols: `__attribute__`, `pure_func`; includes: no external include beyond compiler defaults; macros: `PURE`.

Control flow: the file declares an annotated function/type/object and calls or references it from `main` when needed. Runtime behavior is incidental; the compile result is the detection signal.

State and persistence behavior: no persistent state. Any locals or static examples exist only to force the compiler to parse and type-check the attribute.

Dependencies and integration points: feeds stress-ng portability macros such as inline, noinline, noreturn, pure/const, packed, unused, weak, and returns-nonnull style annotations. Successful probes allow the main code to use stronger compiler hints without breaking other toolchains.

Risks and test signals: compilers may accept an attribute but ignore it, warn under different flags, or require placement on a specific declaration form. The meaningful signal is clean compilation with the configured warning policy.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-attr-pure.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-attr-returns-nonnull.c -->
# sources/test-tools/stress-ng/test/test-attr-returns-nonnull.c

Purpose: compile probe for compiler attribute support for `returns-nonnull`, ensuring stress-ng can annotate functions, types, or objects with the corresponding optimization/diagnostic contract.

Important APIs/types/functions: `__attribute__` syntax or related compiler annotation forms; observed symbols: `__attribute__`, `returns_nonnull_func`; includes: `<stdlib.h>`, `<string.h>`; macros: `RETURNS_NONNULL`.

Control flow: the file declares an annotated function/type/object and calls or references it from `main` when needed. Runtime behavior is incidental; the compile result is the detection signal.

State and persistence behavior: no persistent state. Any locals or static examples exist only to force the compiler to parse and type-check the attribute.

Dependencies and integration points: feeds stress-ng portability macros such as inline, noinline, noreturn, pure/const, packed, unused, weak, and returns-nonnull style annotations. Successful probes allow the main code to use stronger compiler hints without breaking other toolchains.

Risks and test signals: compilers may accept an attribute but ignore it, warn under different flags, or require placement on a specific declaration form. The meaningful signal is clean compilation with the configured warning policy.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-attr-returns-nonnull.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-attr-unused.c -->
# sources/test-tools/stress-ng/test/test-attr-unused.c

Purpose: compile probe for compiler attribute support for `unused`, ensuring stress-ng can annotate functions, types, or objects with the corresponding optimization/diagnostic contract.

Important APIs/types/functions: `__attribute__` syntax or related compiler annotation forms; observed symbols: `__attribute__`, `pure_func`; includes: no external include beyond compiler defaults; macros: `WARN_UNUSED`.

Control flow: the file declares an annotated function/type/object and calls or references it from `main` when needed. Runtime behavior is incidental; the compile result is the detection signal.

State and persistence behavior: no persistent state. Any locals or static examples exist only to force the compiler to parse and type-check the attribute.

Dependencies and integration points: feeds stress-ng portability macros such as inline, noinline, noreturn, pure/const, packed, unused, weak, and returns-nonnull style annotations. Successful probes allow the main code to use stronger compiler hints without breaking other toolchains.

Risks and test signals: compilers may accept an attribute but ignore it, warn under different flags, or require placement on a specific declaration form. The meaningful signal is clean compilation with the configured warning policy.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-attr-unused.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-attr-weak.c -->
# sources/test-tools/stress-ng/test/test-attr-weak.c

Purpose: compile probe for compiler attribute support for `weak`, ensuring stress-ng can annotate functions, types, or objects with the corresponding optimization/diagnostic contract.

Important APIs/types/functions: `__attribute__` syntax or related compiler annotation forms; observed symbols: `__attribute__`, `weak_func`; includes: no external include beyond compiler defaults; macros: `WEAK`.

Control flow: the file declares an annotated function/type/object and calls or references it from `main` when needed. Runtime behavior is incidental; the compile result is the detection signal.

State and persistence behavior: no persistent state. Any locals or static examples exist only to force the compiler to parse and type-check the attribute.

Dependencies and integration points: feeds stress-ng portability macros such as inline, noinline, noreturn, pure/const, packed, unused, weak, and returns-nonnull style annotations. Successful probes allow the main code to use stronger compiler hints without breaking other toolchains.

Risks and test signals: compilers may accept an attribute but ignore it, warn under different flags, or require placement on a specific declaration form. The meaningful signal is clean compilation with the configured warning policy.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-attr-weak.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-backtrace.c -->
# sources/test-tools/stress-ng/test/test-backtrace.c

Purpose: compile probe for glibc `backtrace`/`backtrace_symbols`. It exists to let the stress-ng build detect whether this platform exposes the API, type, constant, header, or library call needed by guarded stressor code.

Important APIs/types/functions: observed call/type/function symbols include `backtrace`, `backtrace_symbols`, `printf`, `free`; includes: `<execinfo.h>`, `<stdlib.h>`, `<stdio.h>`; macros: `_GNU_SOURCE`.

Control flow: `main` declares minimal arguments, invokes or references the target API/type, and returns the result or zero. Invalid descriptors, null-ish arguments, or dummy structures are acceptable because compile/link availability is the primary goal.

State and persistence behavior: any state is local to the probe process. The file does not intentionally create durable resources; when it opens or allocates anything, the scope is limited to proving the symbol and signature are usable.

Dependencies and integration points: this probe contributes one feature bit to stress-ng's generated configuration, enabling or disabling code paths that use `backtrace`. Some probes also require external libraries such as libacl, libbsd, libc realtime/AIO support, or platform-specific headers.

Risks and test signals: successful compilation may not imply the call succeeds at runtime with dummy arguments, sufficient privileges, or all kernels. Failures indicate missing headers, declarations, libraries, constants, or incompatible signatures.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-backtrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-brk.c -->
# sources/test-tools/stress-ng/test/test-brk.c

Purpose: compile probe for the `brk()` heap break syscall wrapper. It exists to let the stress-ng build detect whether this platform exposes the API, type, constant, header, or library call needed by guarded stressor code.

Important APIs/types/functions: observed call/type/function symbols include `brk`; includes: `<unistd.h>`; macros: none.

Control flow: `main` declares minimal arguments, invokes or references the target API/type, and returns the result or zero. Invalid descriptors, null-ish arguments, or dummy structures are acceptable because compile/link availability is the primary goal.

State and persistence behavior: any state is local to the probe process. The file does not intentionally create durable resources; when it opens or allocates anything, the scope is limited to proving the symbol and signature are usable.

Dependencies and integration points: this probe contributes one feature bit to stress-ng's generated configuration, enabling or disabling code paths that use `brk`. Some probes also require external libraries such as libacl, libbsd, libc realtime/AIO support, or platform-specific headers.

Risks and test signals: successful compilation may not imply the call succeeds at runtime with dummy arguments, sufficient privileges, or all kernels. Failures indicate missing headers, declarations, libraries, constants, or incompatible signatures.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-brk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-bsd-wchar.c -->
# sources/test-tools/stress-ng/test/test-bsd-wchar.c

Purpose: compile probe for BSD wide-character support through libbsd headers. It exists to let the stress-ng build detect whether this platform exposes the API, type, constant, header, or library call needed by guarded stressor code.

Important APIs/types/functions: observed call/type/function symbols include `main` only with compile-time expressions; includes: `<stdio.h>`, `<bsd/wchar.h>`; macros: none.

Control flow: `main` declares minimal arguments, invokes or references the target API/type, and returns the result or zero. Invalid descriptors, null-ish arguments, or dummy structures are acceptable because compile/link availability is the primary goal.

State and persistence behavior: any state is local to the probe process. The file does not intentionally create durable resources; when it opens or allocates anything, the scope is limited to proving the symbol and signature are usable.

Dependencies and integration points: this probe contributes one feature bit to stress-ng's generated configuration, enabling or disabling code paths that use `bsd-wchar`. Some probes also require external libraries such as libacl, libbsd, libc realtime/AIO support, or platform-specific headers.

Risks and test signals: successful compilation may not imply the call succeeds at runtime with dummy arguments, sufficient privileges, or all kernels. Failures indicate missing headers, declarations, libraries, constants, or incompatible signatures.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-bsd-wchar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-bsearch.c -->
# sources/test-tools/stress-ng/test/test-bsearch.c

Purpose: compile probe for C library `bsearch`. It exists to let the stress-ng build detect whether this platform exposes the API, type, constant, header, or library call needed by guarded stressor code.

Important APIs/types/functions: observed call/type/function symbols include `cmp`, `bsearch`; includes: `<search.h>`, `<stdlib.h>`; macros: none.

Control flow: `main` declares minimal arguments, invokes or references the target API/type, and returns the result or zero. Invalid descriptors, null-ish arguments, or dummy structures are acceptable because compile/link availability is the primary goal.

State and persistence behavior: any state is local to the probe process. The file does not intentionally create durable resources; when it opens or allocates anything, the scope is limited to proving the symbol and signature are usable.

Dependencies and integration points: this probe contributes one feature bit to stress-ng's generated configuration, enabling or disabling code paths that use `bsearch`. Some probes also require external libraries such as libacl, libbsd, libc realtime/AIO support, or platform-specific headers.

Risks and test signals: successful compilation may not imply the call succeeds at runtime with dummy arguments, sufficient privileges, or all kernels. Failures indicate missing headers, declarations, libraries, constants, or incompatible signatures.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-bsearch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-__clear_cache.c -->
# sources/test-tools/stress-ng/test/test-builtin-__clear_cache.c

Purpose: compile probe for compiler builtin `__clear_cache` or a closely related builtin family used by stress-ng optimized helpers.

Important APIs/types/functions: compiler builtin invocation(s); observed symbols: `__builtin___clear_cache`; includes: no external include beyond compiler defaults; macros: none.

Control flow: `main` prepares simple local operands, invokes the builtin, and returns a value derived from it or zero. The probe intentionally keeps inputs small so compile/link support is isolated from workload behavior.

State and persistence behavior: no persistent state. Only local variables and temporary return values are involved.

Dependencies and integration points: the build uses this result to enable guarded implementations for bit operations, cache management, byte swapping, complex arithmetic, CPU identification, constant folding, or CRC helpers. Failure keeps fallback C code or disables dependent optimizations.

Risks and test signals: builtin names and signatures differ across GCC, Clang, architecture targets, and compiler versions; CPU-specific builtins may also require target flags. Successful compilation is the primary signal, while runtime return values are secondary or ignored.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-__clear_cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-assume-aligned.c -->
# sources/test-tools/stress-ng/test/test-builtin-assume-aligned.c

Purpose: compile probe for compiler builtin `assume-aligned` or a closely related builtin family used by stress-ng optimized helpers.

Important APIs/types/functions: compiler builtin invocation(s); observed symbols: `__builtin_assume_aligned`; includes: no external include beyond compiler defaults; macros: none.

Control flow: `main` prepares simple local operands, invokes the builtin, and returns a value derived from it or zero. The probe intentionally keeps inputs small so compile/link support is isolated from workload behavior.

State and persistence behavior: no persistent state. Only local variables and temporary return values are involved.

Dependencies and integration points: the build uses this result to enable guarded implementations for bit operations, cache management, byte swapping, complex arithmetic, CPU identification, constant folding, or CRC helpers. Failure keeps fallback C code or disables dependent optimizations.

Risks and test signals: builtin names and signatures differ across GCC, Clang, architecture targets, and compiler versions; CPU-specific builtins may also require target flags. Successful compilation is the primary signal, while runtime return values are secondary or ignored.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-assume-aligned.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-bitreverse.c -->
# sources/test-tools/stress-ng/test/test-builtin-bitreverse.c

Purpose: compile probe for compiler builtin `bitreverse` or a closely related builtin family used by stress-ng optimized helpers.

Important APIs/types/functions: compiler builtin invocation(s); observed symbols: `__builtin_bitreverse8`, `__builtin_bitreverse16`, `__builtin_bitreverse32`, `__builtin_bitreverse64`; includes: `<stdint.h>`, `<stdint.h>`; macros: none.

Control flow: `main` prepares simple local operands, invokes the builtin, and returns a value derived from it or zero. The probe intentionally keeps inputs small so compile/link support is isolated from workload behavior.

State and persistence behavior: no persistent state. Only local variables and temporary return values are involved.

Dependencies and integration points: the build uses this result to enable guarded implementations for bit operations, cache management, byte swapping, complex arithmetic, CPU identification, constant folding, or CRC helpers. Failure keeps fallback C code or disables dependent optimizations.

Risks and test signals: builtin names and signatures differ across GCC, Clang, architecture targets, and compiler versions; CPU-specific builtins may also require target flags. Successful compilation is the primary signal, while runtime return values are secondary or ignored.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-bitreverse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-bswap32.c -->
# sources/test-tools/stress-ng/test/test-builtin-bswap32.c

Purpose: compile probe for compiler builtin `bswap32` or a closely related builtin family used by stress-ng optimized helpers.

Important APIs/types/functions: compiler builtin invocation(s); observed symbols: `__builtin_bswap32`; includes: `<stdint.h>`, `<stdlib.h>`; macros: none.

Control flow: `main` prepares simple local operands, invokes the builtin, and returns a value derived from it or zero. The probe intentionally keeps inputs small so compile/link support is isolated from workload behavior.

State and persistence behavior: no persistent state. Only local variables and temporary return values are involved.

Dependencies and integration points: the build uses this result to enable guarded implementations for bit operations, cache management, byte swapping, complex arithmetic, CPU identification, constant folding, or CRC helpers. Failure keeps fallback C code or disables dependent optimizations.

Risks and test signals: builtin names and signatures differ across GCC, Clang, architecture targets, and compiler versions; CPU-specific builtins may also require target flags. Successful compilation is the primary signal, while runtime return values are secondary or ignored.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-bswap32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-clz.c -->
# sources/test-tools/stress-ng/test/test-builtin-clz.c

Purpose: compile probe for compiler builtin `clz` or a closely related builtin family used by stress-ng optimized helpers.

Important APIs/types/functions: compiler builtin invocation(s); observed symbols: `__builtin_clz`; includes: no external include beyond compiler defaults; macros: none.

Control flow: `main` prepares simple local operands, invokes the builtin, and returns a value derived from it or zero. The probe intentionally keeps inputs small so compile/link support is isolated from workload behavior.

State and persistence behavior: no persistent state. Only local variables and temporary return values are involved.

Dependencies and integration points: the build uses this result to enable guarded implementations for bit operations, cache management, byte swapping, complex arithmetic, CPU identification, constant folding, or CRC helpers. Failure keeps fallback C code or disables dependent optimizations.

Risks and test signals: builtin names and signatures differ across GCC, Clang, architecture targets, and compiler versions; CPU-specific builtins may also require target flags. Successful compilation is the primary signal, while runtime return values are secondary or ignored.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-clz.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-clzl.c -->
# sources/test-tools/stress-ng/test/test-builtin-clzl.c

Purpose: compile probe for compiler builtin `clzl` or a closely related builtin family used by stress-ng optimized helpers.

Important APIs/types/functions: compiler builtin invocation(s); observed symbols: `__builtin_clzl`; includes: no external include beyond compiler defaults; macros: none.

Control flow: `main` prepares simple local operands, invokes the builtin, and returns a value derived from it or zero. The probe intentionally keeps inputs small so compile/link support is isolated from workload behavior.

State and persistence behavior: no persistent state. Only local variables and temporary return values are involved.

Dependencies and integration points: the build uses this result to enable guarded implementations for bit operations, cache management, byte swapping, complex arithmetic, CPU identification, constant folding, or CRC helpers. Failure keeps fallback C code or disables dependent optimizations.

Risks and test signals: builtin names and signatures differ across GCC, Clang, architecture targets, and compiler versions; CPU-specific builtins may also require target flags. Successful compilation is the primary signal, while runtime return values are secondary or ignored.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-clzl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-clzll.c -->
# sources/test-tools/stress-ng/test/test-builtin-clzll.c

Purpose: compile probe for compiler builtin `clzll` or a closely related builtin family used by stress-ng optimized helpers.

Important APIs/types/functions: compiler builtin invocation(s); observed symbols: `__builtin_clzll`; includes: no external include beyond compiler defaults; macros: none.

Control flow: `main` prepares simple local operands, invokes the builtin, and returns a value derived from it or zero. The probe intentionally keeps inputs small so compile/link support is isolated from workload behavior.

State and persistence behavior: no persistent state. Only local variables and temporary return values are involved.

Dependencies and integration points: the build uses this result to enable guarded implementations for bit operations, cache management, byte swapping, complex arithmetic, CPU identification, constant folding, or CRC helpers. Failure keeps fallback C code or disables dependent optimizations.

Risks and test signals: builtin names and signatures differ across GCC, Clang, architecture targets, and compiler versions; CPU-specific builtins may also require target flags. Successful compilation is the primary signal, while runtime return values are secondary or ignored.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-clzll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-complex.c -->
# sources/test-tools/stress-ng/test/test-builtin-complex.c

Purpose: compile probe for compiler builtin `complex` or a closely related builtin family used by stress-ng optimized helpers.

Important APIs/types/functions: compiler builtin invocation(s); observed symbols: `__builtin_complex`; includes: `<complex.h>`; macros: none.

Control flow: `main` prepares simple local operands, invokes the builtin, and returns a value derived from it or zero. The probe intentionally keeps inputs small so compile/link support is isolated from workload behavior.

State and persistence behavior: no persistent state. Only local variables and temporary return values are involved.

Dependencies and integration points: the build uses this result to enable guarded implementations for bit operations, cache management, byte swapping, complex arithmetic, CPU identification, constant folding, or CRC helpers. Failure keeps fallback C code or disables dependent optimizations.

Risks and test signals: builtin names and signatures differ across GCC, Clang, architecture targets, and compiler versions; CPU-specific builtins may also require target flags. Successful compilation is the primary signal, while runtime return values are secondary or ignored.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-complex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-constant_p.c -->
# sources/test-tools/stress-ng/test/test-builtin-constant_p.c

Purpose: compile probe for compiler builtin `constant_p` or a closely related builtin family used by stress-ng optimized helpers.

Important APIs/types/functions: compiler builtin invocation(s); observed symbols: `__builtin_constant_p`; includes: no external include beyond compiler defaults; macros: none.

Control flow: `main` prepares simple local operands, invokes the builtin, and returns a value derived from it or zero. The probe intentionally keeps inputs small so compile/link support is isolated from workload behavior.

State and persistence behavior: no persistent state. Only local variables and temporary return values are involved.

Dependencies and integration points: the build uses this result to enable guarded implementations for bit operations, cache management, byte swapping, complex arithmetic, CPU identification, constant folding, or CRC helpers. Failure keeps fallback C code or disables dependent optimizations.

Risks and test signals: builtin names and signatures differ across GCC, Clang, architecture targets, and compiler versions; CPU-specific builtins may also require target flags. Successful compilation is the primary signal, while runtime return values are secondary or ignored.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-constant_p.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-cpu-is-power10.c -->
# sources/test-tools/stress-ng/test/test-builtin-cpu-is-power10.c

Purpose: compile probe for compiler builtin `cpu-is-power10` or a closely related builtin family used by stress-ng optimized helpers.

Important APIs/types/functions: compiler builtin invocation(s); observed symbols: `__builtin_cpu_is`; includes: no external include beyond compiler defaults; macros: none.

Control flow: `main` prepares simple local operands, invokes the builtin, and returns a value derived from it or zero. The probe intentionally keeps inputs small so compile/link support is isolated from workload behavior.

State and persistence behavior: no persistent state. Only local variables and temporary return values are involved.

Dependencies and integration points: the build uses this result to enable guarded implementations for bit operations, cache management, byte swapping, complex arithmetic, CPU identification, constant folding, or CRC helpers. Failure keeps fallback C code or disables dependent optimizations.

Risks and test signals: builtin names and signatures differ across GCC, Clang, architecture targets, and compiler versions; CPU-specific builtins may also require target flags. Successful compilation is the primary signal, while runtime return values are secondary or ignored.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-cpu-is-power10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-cpu-is-power11.c -->
# sources/test-tools/stress-ng/test/test-builtin-cpu-is-power11.c

Purpose: compile probe for compiler builtin `cpu-is-power11` or a closely related builtin family used by stress-ng optimized helpers.

Important APIs/types/functions: compiler builtin invocation(s); observed symbols: `__builtin_cpu_is`; includes: no external include beyond compiler defaults; macros: none.

Control flow: `main` prepares simple local operands, invokes the builtin, and returns a value derived from it or zero. The probe intentionally keeps inputs small so compile/link support is isolated from workload behavior.

State and persistence behavior: no persistent state. Only local variables and temporary return values are involved.

Dependencies and integration points: the build uses this result to enable guarded implementations for bit operations, cache management, byte swapping, complex arithmetic, CPU identification, constant folding, or CRC helpers. Failure keeps fallback C code or disables dependent optimizations.

Risks and test signals: builtin names and signatures differ across GCC, Clang, architecture targets, and compiler versions; CPU-specific builtins may also require target flags. Successful compilation is the primary signal, while runtime return values are secondary or ignored.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-cpu-is-power11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-cpu-is-power9.c -->
# sources/test-tools/stress-ng/test/test-builtin-cpu-is-power9.c

Purpose: compile probe for compiler builtin `cpu-is-power9` or a closely related builtin family used by stress-ng optimized helpers.

Important APIs/types/functions: compiler builtin invocation(s); observed symbols: `__builtin_cpu_is`; includes: no external include beyond compiler defaults; macros: none.

Control flow: `main` prepares simple local operands, invokes the builtin, and returns a value derived from it or zero. The probe intentionally keeps inputs small so compile/link support is isolated from workload behavior.

State and persistence behavior: no persistent state. Only local variables and temporary return values are involved.

Dependencies and integration points: the build uses this result to enable guarded implementations for bit operations, cache management, byte swapping, complex arithmetic, CPU identification, constant folding, or CRC helpers. Failure keeps fallback C code or disables dependent optimizations.

Risks and test signals: builtin names and signatures differ across GCC, Clang, architecture targets, and compiler versions; CPU-specific builtins may also require target flags. Successful compilation is the primary signal, while runtime return values are secondary or ignored.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-cpu-is-power9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-crc16_data16.c -->
# sources/test-tools/stress-ng/test/test-builtin-crc16_data16.c

Purpose: compile probe for compiler builtin `crc16_data16` or a closely related builtin family used by stress-ng optimized helpers.

Important APIs/types/functions: compiler builtin invocation(s); observed symbols: `__builtin_crc16_data8`; includes: `<stdint.h>`; macros: none.

Control flow: `main` prepares simple local operands, invokes the builtin, and returns a value derived from it or zero. The probe intentionally keeps inputs small so compile/link support is isolated from workload behavior.

State and persistence behavior: no persistent state. Only local variables and temporary return values are involved.

Dependencies and integration points: the build uses this result to enable guarded implementations for bit operations, cache management, byte swapping, complex arithmetic, CPU identification, constant folding, or CRC helpers. Failure keeps fallback C code or disables dependent optimizations.

Risks and test signals: builtin names and signatures differ across GCC, Clang, architecture targets, and compiler versions; CPU-specific builtins may also require target flags. Successful compilation is the primary signal, while runtime return values are secondary or ignored.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-crc16_data16.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-crc16_data8.c -->
# sources/test-tools/stress-ng/test/test-builtin-crc16_data8.c

Purpose: compile probe for compiler builtin `crc16_data8` or a closely related builtin family used by stress-ng optimized helpers.

Important APIs/types/functions: compiler builtin invocation(s); observed symbols: `__builtin_crc16_data8`; includes: `<stdint.h>`; macros: none.

Control flow: `main` prepares simple local operands, invokes the builtin, and returns a value derived from it or zero. The probe intentionally keeps inputs small so compile/link support is isolated from workload behavior.

State and persistence behavior: no persistent state. Only local variables and temporary return values are involved.

Dependencies and integration points: the build uses this result to enable guarded implementations for bit operations, cache management, byte swapping, complex arithmetic, CPU identification, constant folding, or CRC helpers. Failure keeps fallback C code or disables dependent optimizations.

Risks and test signals: builtin names and signatures differ across GCC, Clang, architecture targets, and compiler versions; CPU-specific builtins may also require target flags. Successful compilation is the primary signal, while runtime return values are secondary or ignored.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/test/test-builtin-crc16_data8.c -->
