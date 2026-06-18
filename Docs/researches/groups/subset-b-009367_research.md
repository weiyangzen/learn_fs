# subset-b-009367 Research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-dev.c -->
# sources/test-tools/stress-ng/stress-dev.c

Purpose: implements the `dev` stressor, which walks `/dev` or a user-selected `--dev-file` and exercises character/block devices through safe-ish open, poll/select, mmap, read/lseek/fsync, fcntl, and many device-specific ioctl paths. It is primarily Linux-oriented and falls back to `stress_unimplemented` when pthread/poll support is unavailable.

Important APIs/types/functions: `dev_state_t` stores shared flags for SCSI checks and open success/failure; `dev_info_t` stores path/name/random ordering plus a pointer into shared state; `stress_dev_func_t` maps device path prefixes to handler functions in `dev_funcs[]`. Major handlers cover block devices, SCSI/sg, TTY/console, device mapper, V4L2, random, RTC, memory devices, CD/DVD, HID, HPET, parallel port, USB, input/uinput, KVM, framebuffer, cpuid/msr, autofs, ALSA control, PTP, floppy, hwrng, and EFI-adjacent sysfs device files. `stress_dev_rw()` performs the common per-device exercise. `stress_dev_files()` coordinates each list pass. `stress_dev_infos_get()` and `stress_sys_dev_infos_get()` discover `/dev` and `/sys/dev`. `stress_dev()` owns setup, fork/thread lifecycle, shared mmap state, and final reporting.

Control flow: `stress_dev()` validates `--dev-file` or recursively scans `/dev`, skips dangerous names such as watchdogs, current tty, Xen HPET, and high-numbered device siblings, randomizes the list, allocates shared `dev_state_t` storage, then repeatedly forks a child. The child initializes process-shared spinlocks, starts up to four helper pthreads, and also runs `stress_dev_files()` in the controlling thread. A shared `pthread_dev_info` pointer tells helpers which device to exercise; each helper loops through `stress_dev_rw()`. Each device pass opens with timeouts, checks block/char mode, performs generic probes, invokes prefix-matched `dev_funcs[]`, tries alternate open flags, and increments bogo operations.

State and persistence behavior: no durable repository or system state is intentionally stored. Runtime state lives in anonymous shared mmap (`dev_state_t[]`) so parent/child can remember failed opens, successful opens, and SCSI classification. Process-shared spinlocks serialize current-device pointer updates and parallel-port claim/release. Some handlers temporarily restore mutable device settings after read/set ioctls; CD-ROM, TTY, console, framebuffer, block, and parallel-port paths intentionally try current-value set operations and invalid calls for coverage. `stress_dev_procname()` changes process title for stuck-device diagnostics unless name keeping is requested.

Dependencies and integration points: depends heavily on stress-ng core helpers (`stress_try_open*`, temp/process/scheduler/OOM helpers, metrics, random, fdinfo, capability checks, pthread shims) and compile-time `HAVE_*` probes for Linux kernel headers. Integration is through `stress_dev_info` with classifier `CLASS_DEV | CLASS_OS` and option `dev-file`.

Risks: this file touches real devices. Risk is managed by avoidance lists, nonblocking opens, time-limited try-open/ioctl wrappers, privileged-action checks, and skipped known-bad cases, but some ioctls can still tickle driver bugs or transiently change device settings. The shared state is simple bool fields, so concurrent updates are intentionally approximate. Prefix matching can route broad paths to handlers, so new device names need careful review.

Test signals: build with varied Linux header availability, run `stress-ng --dev 1 --timeout ...` as non-root and root, run targeted `--dev-file /dev/null`, `/dev/random`, `/dev/mapper/control`, and tty-like files where available, and check final log line reporting opened/exercised devices. Useful failures include unexpected non-device rejection, stuck-open timeouts, process exits from child worker, and dmesg warnings from ioctl coverage.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-dfp.c -->
# sources/test-tools/stress-ng/stress-dfp.c

Purpose: implements the `dfp` CPU/FP stressor for compiler-supported decimal floating point types `_Decimal32`, `_Decimal64`, and `_Decimal128`. It repeatedly performs add, subtract, multiply, and divide loops and reports per-method throughput.

Important APIs/types/functions: `dfp_data_t` stores per-element initial values, two result slots, add/reverse-add, and multiply/reverse-multiply values for each enabled decimal type. Macro generators `STRESS_DFP_ADD/SUB/MUL/DIV` create optimized method functions. `stress_dfp_funcs[]` maps method names such as `df32add` and `df128div` to function pointers and decimal type IDs. `stress_dfp_call_method()` invokes methods, updates `stress_dfp_metrics`, and optionally verifies two runs. `stress_dfp_all()` iterates all concrete methods. `stress_dfp()` allocates data, initializes operands, runs the selected method, and emits metrics.

Control flow: after SIGILL handling and mmap allocation, `stress_dfp()` reads `--dfp-method` defaulting to `all`, initializes all decimal fields from random values, synchronizes start, clears metrics, and loops while `stress_continue(args)`. Each call performs `DFP_ELEMENTS * LOOPS_PER_CALL` logical operations per metric update. At shutdown it emits `Mdfp-ops per sec` metrics for every method with duration/count.

State and persistence behavior: state is process-local anonymous mmap named `dfp-data`; metrics use a static `stress_dfp_metrics[]` array reset at start. No filesystem state is created. Verification compares duplicate result slots using `memcmp` for exact decimal representation, but skips verification if a stop signal interrupts the second run.

Dependencies and integration points: relies on compiler feature macros `HAVE_Decimal32/64/128`, stress-ng mmap/madvise/target-clones/signal/metrics helpers, and stressor registration through `stress_dfp_info` with `CLASS_CPU | CLASS_FP | CLASS_COMPUTE | CLASS_HOT`. If no decimal types exist, the stressor is registered as unimplemented while still exposing the method option.

Risks: decimal floating point support is compiler- and architecture-dependent; invalid assumptions about type availability or exact representation can break verification. Division loops check `stress_continue_flag()` because they may be slower. Metrics for the `all` pseudo-method are distributed to concrete methods, so method-index invariants matter.

Test signals: compile on toolchains with none, some, and all decimal types; run `--dfp-method all` and each concrete method with and without `--verify`; inspect per-method metrics and confirm unimplemented messaging on unsupported builds.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-dfp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-dir.c -->
# sources/test-tools/stress-ng/stress-dir.c

Purpose: implements the `dir` filesystem stressor, creating, reading, renaming, and deleting many directories under a stress-ng temporary directory while exercising directory-specific error paths.

Important APIs/types/functions: `stress_dir_sync()`, `stress_dir_flock()`, `stress_dir_truncate()`, and `stress_dir_mmap()` probe directory fd behavior. `stress_dir_read()` opens/stat entries. `stress_dir_rename()` renames each child out and back to exercise directory iteration under mutation. `stress_mkdir()` alternates between `mkdir()` and `mkdirat()`. `stress_invalid_mkdir*()` and `stress_invalid_rmdir()` exercise expected failure paths. `stress_dir_readdir()` verifies `rewinddir()` sees files created after `opendir()`. `stress_dir()` owns the main loop.

Control flow: the stressor creates a temp directory, optionally opens it with `O_DIRECTORY`, forks a concurrent reader, then loops. Each iteration mmaps/flocks/truncates the directory, creates `dir-dirs` children using gray-code filenames, runs invalid mkdir/rmdir cases, reads and renames entries, verifies readdir/rewinddir behavior, removes created directories, fsyncs/syncs, and increments bogo counts. On stop, it tidies partial work and kills the reader child.

State and persistence behavior: all persistent filesystem effects are confined to the stress-ng temp directory and removed with `stress_dir_tidy()` plus `stress_fs_temp_dir_rm_args()`. Runtime counters are local. The forked reader does not share explicit state beyond the directory contents.

Dependencies and integration points: uses stress-ng filesystem naming/temp helpers, `core-killpid`, `stress_sync_start_wait`, and option `dir-dirs` bounded from 64 to 65536. Registered as `stress_dir_info`, classifier `CLASS_FILESYSTEM | CLASS_OS`, `VERIFY_ALWAYS`.

Risks: filesystem-specific behavior around directory mmap/truncate/ftruncate, concurrent readdir under rename, and `d_reclen` can differ by platform. High `dir-dirs` values can hit `ENOSPC`, `ENOMEM`, or `EMLINK`, which are treated as expected capacity limits. Cleanup must handle partial creation when stop arrives.

Test signals: run with minimized/maximized `dir-dirs`, short timeout, and `--verify`; confirm no leftover temp directories, no zero-sized dirent failures, and no unexpected rename/readdir verification failures.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-dirdeep.c -->
# sources/test-tools/stress-ng/stress-dirdeep.c

Purpose: implements `dirdeep`, a recursive directory-depth and inode-consumption stressor. It creates a deep tree with short directory names, symlinks, hardlinks, and optional per-directory files, then repeatedly traverses/exercises it before deleting it.

Important APIs/types/functions: `stress_dirdeep_inodes()` parses absolute or percent inode limits. `stress_dirdeep_make()` recursively creates directories, top-level link target, symlinks, hardlinks, optional files with fallocate, and `linkat()` variants. `stress_dir_exercise()` traverses with `scandir()`, touches file atimes with `open()`/`futimens()`, and occasionally fsyncs/syncfs. `stress_dir_tidy()` recursively removes files and directories in reverse sorted order. `stress_dirdeep()` ties options and lifecycle together.

Control flow: options determine bytes, subdirectories per level, files per level, and inode limit. The stressor records initial free inodes, builds a root temp path and link target, synchronizes start, recursively creates until path length, stop flag, filesystem limits, or inode budget halts creation, then loops traversing the tree until stop. Deinit recursively removes everything and reports exercised inode count.

State and persistence behavior: all created data is under the stress-ng temp path. Inode state is inferred from `stress_fs_available_inodes_get()` when available, with a local estimate fallback. `static bool tidy_info` suppresses repeated cleanup progress messages across invocations in the process.

Dependencies and integration points: depends on stress-ng temp path helpers, inode/free-space helpers, setting callbacks, sync/fallocate shims, and optional `linkat`, `unlinkat`, `futimens`, and `syncfs`. Registered with `dirdeep-bytes`, `dirdeep-dirs`, `dirdeep-inodes`, and `dirdeep-files`.

Risks: high branch factors and file counts can consume many inodes and path space quickly. The recursion relies on single-character directory names to preserve path headroom, but still stops on path length. Hardlink/symlink/linkat behavior varies across filesystems and permissions; expected capacity/permission errors stop creation without marking failure.

Test signals: run with low inode/file settings and with percent inode limits; verify cleanup removes the root tree, debug output reports inode use, and larger settings stop gracefully on ENOSPC/EDQUOT/EMLINK/ENAMETOOLONG.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-dirdeep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-dirmany.c -->
# sources/test-tools/stress-ng/stress-dirmany.c

Purpose: implements `dirmany`, which stresses directory scalability by creating and removing many files with progressively longer names and optional allocated file sizes.

Important APIs/types/functions: `stress_dirmany_filename()` builds deterministic names from the temp directory, a run-length of `x`, and a 16-digit hex index. `stress_dirmany_create()` creates files until time budget, stop, name-length limit, or filesystem failure; it can fallocate requested bytes and validates creation with `stat()`. `stress_dirmany_remove()` unlinks the generated sequence. `stress_dirmany()` owns option handling and metrics.

Control flow: the stressor creates a temp directory, resolves `--dirmany-bytes` with maximize/minimize behavior, synchronizes start, and loops create/remove phases. Creation uses about 60% of remaining timeout so cleanup has time. After removal, the next index continues unless it grows beyond one billion, where it wraps to avoid overflow.

State and persistence behavior: filesystem state is temporary files under a stress-ng temp directory, removed after every cycle and at final temp-dir removal. Runtime state tracks `i_start`, total created, max valid filename length, and timing accumulators. No durable state is kept.

Dependencies and integration points: depends on stress-ng temp helpers, `core-builtin`, fallocate shims, metrics, timeout globals, and `dirmany-bytes` option. Registered as `CLASS_FILESYSTEM | CLASS_OS` with `VERIFY_ALWAYS`.

Risks: filename-length probing treats `ENAMETOOLONG` by backing off; other open failures end the create phase. Large `dirmany-bytes` can consume disk space quickly despite timed removal. `stat()` failures other than `ENOMEM` are verification failures.

Test signals: run with default zero-byte files, small nonzero `--dirmany-bytes`, and maximize/minimize modes; inspect metrics for create/remove percentage and rates, and confirm no leftover temp files after interruption.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-dirmany.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-dnotify.c -->
# sources/test-tools/stress-ng/stress-dnotify.c

Purpose: implements `dnotify`, a Linux legacy directory notification stressor that verifies DN_* events are delivered through `F_NOTIFY` and realtime signals.

Important APIs/types/functions: `stress_dnotify_supported()` reads `/proc/sys/fs/dir-notify-enable`. `dnotify_handler()` captures `si_fd` from `SIGRTMIN+1`. `dnotify_exercise()` opens the watched directory, sets `F_SETSIG`, enables `F_NOTIFY` with optional `DN_MULTISHOT`, runs a helper, waits up to two seconds, validates the delivered fd, disables notifications, and closes. Helpers cover attribute, access, modify, create, delete, and rename events using `mk_file()`/`rm_file()`.

Control flow: `stress_dnotify()` installs the realtime signal handler and ignores stray SIGIO, creates a temp directory, synchronizes start, then repeatedly invokes all `dnotify_stressors[]`. Any helper failure exits via tidy with `EXIT_FAILURE`; otherwise each full pass increments bogo operations.

State and persistence behavior: `static volatile int dnotify_fd` is the only event state and is reset before each helper. Temporary files are created inside the stress-ng temp directory and removed immediately after each event, with final directory removal in deinit.

Dependencies and integration points: requires `F_NOTIFY` and `sys/select.h`; otherwise registers as unimplemented. Uses stress-ng signal/temp helpers, file helpers, and classifier `CLASS_FILESYSTEM | CLASS_OS` with `VERIFY_ALWAYS`.

Risks: dnotify is legacy and may be disabled or absent in kernels. Signal delivery is asynchronous, so the two-second polling window is a functional assumption. The code validates unexpected fd values but does not fail if no event arrives before timeout, which reflects stress coverage more than strict notification testing.

Test signals: run on a Linux kernel with dnotify enabled, confirm all event helpers loop without fd mismatch failures, and check skip messages when CONFIG_DNOTIFY or `/proc/sys/fs/dir-notify-enable` is unavailable.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-dnotify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-dup.c -->
# sources/test-tools/stress-ng/stress-dup.c

Purpose: implements `dup`, which stresses file descriptor duplication and closure through `dup`, `dup2`, `dup3`, and `fcntl(F_DUPFD)`, with an optional Linux race reproducer for `dup2`/open `EBUSY`.

Important APIs/types/functions: `info_t` stores race context in shared mmap, including fd targets, FIFO path, clone pid, counts, and clone stack. `stress_dup2_race_clone()` shares the fd table and races `dup2()` against a blocking FIFO open. `static_dup2_child()` sets a short interval timer and manages the clone. `stress_dup2_race()` isolates the race in a forked process. `stress_dup()` performs the main fd duplication loops and metrics.

Control flow: the stressor maps race context and creates a temp directory when supported, opens `/dev/zero`, synchronizes start, and loops filling a static fd array up to the process file limit capped at 65536. For each fd it performs valid and invalid dup/dup3/dup2 operations, same-fd `dup2` verification, optional `F_DUPFD`, optional race pass, and bogo increment. It then closes the opened range and repeats.

State and persistence behavior: fd state is process-local in `fds[]`; race counts live in shared anonymous mmap and are logged at cleanup. A FIFO is created under the stress-ng temp directory for the race and removed on tidy. Metrics record total dup calls and average nanoseconds per dup call.

Dependencies and integration points: depends on stress-ng fd-limit, bad-fd, mmap, killpid, temp, timing, and metrics helpers. Race path requires Linux `clone`, `mkfifo`, `CLONE_VM`, and `CLONE_FILES`. Registered as `CLASS_FILESYSTEM | CLASS_OS`, `VERIFY_ALWAYS`.

Risks: high file limits can create many descriptors; cleanup through `stress_fs_close_fds()` is critical. Race code intentionally shares fd tables and uses timers/signals, so it is Linux-specific and isolated in a child to protect the parent. `dup3` availability is detected through `ENOSYS` fallback.

Test signals: run with low/high `ulimit -n`, verify metrics are emitted, no fd leaks occur, same-fd `dup2` failures are reported, and Linux builds log race attempts without wedging on FIFO open.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-dup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-dynlib.c -->
# sources/test-tools/stress-ng/stress-dynlib.c

Purpose: implements `dynlib`, which stresses dynamic loader operations by repeatedly opening known C library DSOs, resolving symbols, touching resolved code bytes, and closing handles.

Important APIs/types/functions: `stress_lib_info_t` maps compile-time GNU library names from `<gnu/lib-names.h>` to representative symbols. `libnames[]` includes math, pthread, resolver, NSS, rt, util, and related libraries when macros exist. `stress_segvhandler()` uses `siglongjmp` to recover if touching a resolved pointer faults. `stress_dynlib()` owns the dlopen/dlsym/dlclose loop and metric.

Control flow: the stressor installs a SIGSEGV handler, synchronizes start, and loops. Each iteration randomly chooses lazy/now and global/local flags, calls `dlopen()` for each configured library, clears errors, times `dlsym()` lookups for opened handles, reads one byte through `stress_put_uint8()` when a symbol is found, closes all handles, and increments bogo operations.

State and persistence behavior: state is local handle array plus `sigjmp_buf`. No filesystem output or durable state is created. Every iteration closes handles even after a SIGSEGV jump.

Dependencies and integration points: requires `HAVE_LIB_DL` and non-static build; otherwise registers unimplemented. Integrates through `stress_dynlib_info` with classifier `CLASS_OS` and metric `nanosecs per dlsym lookup`.

Risks: symbol sets and GNU DSO macros vary by libc and distribution. Touching function bytes assumes readable mappings, guarded by SIGSEGV recovery. Static builds and non-GNU lib naming cannot exercise this stressor.

Test signals: build dynamic and static variants, run under glibc systems with different available libraries, confirm no leaked handles through repeated runs, and inspect dlsym latency metric.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-dynlib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-easy-opcode.c -->
# sources/test-tools/stress-ng/stress-easy-opcode.c

Purpose: implements `easy-opcode`, a CPU stressor that generates executable pages filled with random simple architecture-specific opcodes plus a return instruction, then repeatedly executes the buffer in a child process.

Important APIs/types/functions: `stress_easy_opcode_t` describes byte sequences. `easy_opcodes[]` is selected by architecture/endian macros and `HAVE_MPROTECT`. `stress_easy_opcode_fill()` writes random easy opcodes into a buffer and appends `stress_ret_opcode`. `stress_easy_opcode_state_t` stores shared bogo count and opcode count. `stress_easy_opcode()` manages mmap, mprotect, fork, execution loop, and metric.

Control flow: after verifying return-opcode support, the stressor maps shared state and private opcode pages with guard pages. It forks a child each cycle; the child protects guard pages, writes opcodes into the executable region, switches it to `PROT_READ | PROT_EXEC`, flushes I-cache, then calls the buffer repeatedly until stop or max ops. The parent waits and copies child bogo count to stress-ng. Final metric is easy opcodes executed per second.

State and persistence behavior: all state is anonymous mmap; no files are created. The child updates shared `state->bogo_ops` and `state->ops`. On x86 it emits `cld` after buffer execution to restore direction flag because some allowed opcodes manipulate flags.

Dependencies and integration points: uses architecture macros, `core-asm-ret`, mmap/mprotect, fork/killpid/scheduler helpers, and stress-ng metrics. Unsupported architectures or missing `mprotect()` register unimplemented.

Risks: generated machine code is inherently architecture-sensitive. The opcode table must only contain safe non-privileged instructions and must preserve control flow to the appended return. W^X, SELinux, or hardened kernels may reject executable anonymous mappings. Child isolation prevents a bad opcode from directly corrupting parent state.

Test signals: build on supported architectures, run short timeouts, verify nonzero opcode-rate metric, and ensure unsupported architectures report unimplemented rather than failing at runtime.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-easy-opcode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-efivar.c -->
# sources/test-tools/stress-ng/stress-efivar.c

Purpose: implements `efivar`, which reads UEFI variable entries from Linux sysfs (`/sys/firmware/efi/efivars` or legacy `/sys/firmware/efi/vars`) to stress EFI variable filesystem read paths and related fd operations.

Important APIs/types/functions: `stress_efi_var_t` mirrors legacy raw variable layout. `efi_var_ignore()` skips dot entries and sensitive/control variables. `guid_to_str()` and `efi_get_varname()` decode legacy raw metadata. `efi_get_data()` reads individual legacy fields. `efi_read_variable()` reads a variable file, gathers fdinfo, probes lseek/mmap/ioctl helpers, and optionally gets/sets FS flags. `efi_vars_get()` iterates cached dentries. `stress_efivar_supported()` checks sysfs availability/capability. `stress_efivar()` handles scanning, shared ignore map, forked worker, metrics, and cleanup.

Control flow: support selection prefers `efivars` over legacy `vars`. At runtime the stressor scans the chosen directory, maps a shared `efi_ignore[]` bitmap, synchronizes, then forks a child. The child applies failure/scheduler/OOM settings and repeatedly calls `efi_vars_get()`, which skips ignored names, reads data through the appropriate backend, marks failing or empty legacy entries ignored, increments bogo count, and accumulates read metrics.

State and persistence behavior: directory entries are cached in memory; per-variable ignore state lives in shared anonymous mmap named `efi-ignore-state`. The stressor is read-oriented, but `efi_read_variable()` may call `FS_IOC_SETFLAGS` with the existing flags value, intended to be non-mutating. No EFI variables are created or deleted.

Dependencies and integration points: Linux-only except Alpha exclusion; uses capabilities checks, OOM and killpid helpers, madvise/signal helpers, sysfs file reads, fdinfo, and metrics. Registered as `CLASS_OS` with `VERIFY_ALWAYS`.

Risks: EFI variable access can require privileges and may expose firmware/kernel bugs. Even read-like operations on efivarfs are sensitive; the code avoids `new_var`, `del_var`, `MokListRT`, writes no data, and uses a child for containment. Directory contents can change while scanned, so open/read failures are usually ignored or mark entries ignored.

Test signals: run on systems with no EFI, legacy vars, and efivars; verify support skip messages, raw data read rate metrics, no variable mutations, and correct cleanup of dirent lists and shared ignore mmap.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-efivar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-eigen-ops.c -->
# sources/test-tools/stress-ng/stress-eigen-ops.c

Purpose: intentionally empty C translation unit associated with the Eigen stressor. It preserves a source/build placeholder while actual Eigen operations live in `stress-eigen-ops.cpp` and declarations in `stress-eigen-ops.h`.

Important APIs/types/functions: none. The only content is license text and an `/* Intentionally empty */` comment.

Control flow: none.

State and persistence behavior: none.

Dependencies and integration points: may be included in source manifests or build systems that expect a `.c` companion for stressor organization, but it exports no symbols and depends on no headers.

Risks: low. The main risk is accidental addition of conflicting C definitions for functions implemented with `extern "C"` in the C++ file.

Test signals: build should compile this file as a no-op and produce no duplicate symbols. Functional Eigen testing belongs to `stress-eigen.c` and `stress-eigen-ops.cpp`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-eigen-ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-eigen-ops.cpp -->
# sources/test-tools/stress-ng/stress-eigen-ops.cpp

Purpose: provides the C-callable C++ Eigen operation implementations used by the `eigen` stressor: matrix addition, multiplication, transpose, inverse, and determinant across `long double`, `double`, and `float`.

Important APIs/types/functions: templated helpers `eigen_add<T>`, `eigen_multiply<T>`, `eigen_transpose<T>`, `eigen_inverse<T>`, and `eigen_determinant<T>` allocate random dynamic Eigen matrices, time an operation, repeat it, and verify the result against `THRESHOLD`. The `extern "C"` block exports fifteen functions declared in the header, such as `eigen_add_double()` and `eigen_determinant_float()`.

Control flow: each exported function simply instantiates the matching template. Each template catches all C++ exceptions and returns `-1` for library/resource failure, `EXIT_FAILURE` for verification mismatch, or `EXIT_SUCCESS`. Durations and operation counts are accumulated through caller-provided pointers for stress-ng metrics.

State and persistence behavior: all matrices are stack/local Eigen objects with heap storage owned by Eigen and freed by normal C++ destruction. No static mutable state and no filesystem state are used.

Dependencies and integration points: compiled only when `HAVE_EIGEN` is defined. Includes `config.h`, `stress-eigen-ops.h`, and `<eigen3/Eigen/Dense>`, and imports C `stress_time_now()`. The C ABI avoids C++ name mangling for calls from `stress-eigen.c`.

Risks: large matrix sizes can cause allocation failures or expensive inverses/determinants. Exact repeatability depends on Eigen deterministic operations over identical inputs; threshold comparisons handle normal FP error. Catch-all exception handling maps failures to skip/resource behavior in the C wrapper.

Test signals: build with and without Eigen/g++; run each `--eigen-method`, check duration/count increments, verify failures are reported for mismatches, and confirm C/C++ linkage produces all expected symbols.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-eigen-ops.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-eigen-ops.h -->
# sources/test-tools/stress-ng/stress-eigen-ops.h

Purpose: declares the C ABI used by `stress-eigen.c` to call Eigen matrix operation implementations compiled from `stress-eigen-ops.cpp`.

Important APIs/types/functions: includes `<stdlib.h>` for `size_t` and declares fifteen functions grouped by operation and scalar type: add, multiply, transpose, inverse, and determinant for long double, double, and float. Every function takes `const size_t size`, `double *duration`, and `double *count`, and returns an int status.

Control flow: none in the header; it defines the contract consumed by the C stressor.

State and persistence behavior: none.

Dependencies and integration points: protected by `STRESS_EIGEN_OPS_H`. It is included inside an `extern "C"` region by the C++ implementation and directly by the C stressor. The return convention is shared: success, failure, or negative library/resource failure.

Risks: prototypes must stay synchronized with the C++ exports and the method table in `stress-eigen.c`. Adding a new operation requires updating all three files coherently.

Test signals: compile/link with `HAVE_EIGEN`; missing or mismatched prototypes surface as compile or link errors. Runtime behavior is tested through `stress-eigen.c`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-eigen-ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-eigen.c -->
# sources/test-tools/stress-ng/stress-eigen.c

Purpose: implements the C-side `eigen` stressor that selects Eigen matrix methods, controls matrix size, runs operations via the C++ bridge, records per-method metrics, and registers stress-ng options.

Important APIs/types/functions: `stress_eigen_func_t` is the common function pointer type for bridge calls. `stress_eigen_method_info_t` maps method names to functions. `eigen_methods[]` contains `all` plus all scalar/operation combinations. `stress_eigen_method()` exposes method names to option parsing. `stress_eigen_all()` rotates through concrete methods for the `all` pseudo-method. `stress_eigen_exercise()` runs the selected method loop, handles return codes, emits per-method metrics, and computes a geometric mean debug rate. `stress_eigen()` handles settings and lifecycle.

Control flow: the stressor reads `--eigen-method` and `--eigen-size` with minimize/maximize bounds, synchronizes start, and calls `stress_eigen_exercise()`. The exercise loop calls the selected function until stop. When method zero is selected, `method_all_index` advances across concrete methods each iteration. After the loop, metrics are emitted for methods that recorded duration.

State and persistence behavior: `current_method`, `method_all_index`, and static `eigen_metrics[]` are process-local runtime state. No filesystem state is created. Matrix allocation and verification live in the C++ file.

Dependencies and integration points: requires `HAVE_EIGEN`; otherwise registers as unimplemented with reason `eigen C++ library, headers or g++ compiler not used`. Uses stress-ng option parsing, process state, metrics, and math `frexp/pow`. Registered as `CLASS_CPU | CLASS_FP | CLASS_COMPUTE`, `VERIFY_ALWAYS`.

Risks: method table order must match the `all` rotation assumption that concrete methods start at index 1. Large sizes up to 1024 can be very costly, especially inverse and determinant. Return `-1` from the C++ bridge is treated as resource/library skip; `EXIT_FAILURE` is a verification failure.

Test signals: run `--eigen-method all` and each named method at small sizes, run maximize/minimize size modes, confirm per-method metrics include matrix size, and build without Eigen to validate unimplemented registration.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-eigen.c -->
