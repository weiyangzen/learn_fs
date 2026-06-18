# subset-b-009369 research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fd-abuse.c -->
## sources/test-tools/stress-ng/stress-fd-abuse.c

Purpose: implements the `fd-abuse` stressor, a broad file-descriptor abuse matrix that opens many descriptor kinds once, forks, and repeatedly applies many valid, invalid, and borderline operations to those descriptors. It is intended to shake out kernel descriptor, file, socket, pipe, timer, pidfd, inotify, mmap, fcntl, splice, and vector I/O paths.

Important APIs/types/functions: `stress_fd_t` carries an `fd` plus read/write/send/receive capability flags. `open_func_t` and `fd_func_t` drive the two operation tables. `open_funcs[]` covers bad fds, `/dev/null`, `/dev/zero`, temp files with many `O_*` variants, pipes, `pipe2()`, `eventfd()`, `memfd_create()`, `memfd_secret()`, many socket families, `socketpair()`, `O_TMPFILE`, `userfaultfd`, `inotify_init()`, `/dev/ptmx`, `timerfd_create()`, `pidfd_open()`, and `epoll_create()`. `fd_funcs[]` covers `setsockopt`, seeks, dup variants, binds, select/poll, mmap, inotify watches, timerfd, pidfd signal, `ioctl(FIOQSIZE)`, `getdents`, stat, truncate, fadvise, listen/accept/shutdown, syncs, chmod/times, locks, fcntl flags, leases, namespace, xattrs, vmsplice, scalar/vector reads and writes, socket send/receive, sendfile, copy-file-range, and splice.

Control flow: `stress_fd_abuse()` installs SIGIO/SIGPIPE ignore handlers, creates a temp filename when possible, synchronizes workers, and runs `stress_fd_abuse_process()` via `stress_oomable_child()`. The child process opens all available descriptor classes, forks once so parent and child operate on the same inherited fd set, walks every descriptor through every operation, then runs random descriptor-operation pairs until `stress_continue()` stops. Only the parent side increments bogo operations; the fork child exits directly.

State and persistence behavior: state is the static temp filename, the global current time used to rate-limit expensive calls, and the open descriptor array. The stressor creates a temporary directory/file and removes them during deinit. It intentionally mutates descriptor flags, offsets, file contents, locks, leases, and socket state, but it is meant to leave no durable files.

Dependencies and integration points: heavily conditional on platform feature macros and stress-ng shims such as `shim_close_range`, `shim_pidfd_send_signal`, `shim_copy_file_range`, temp-file helpers, OOM child handling, random number helpers, and metrics/bogo infrastructure. It registers as `CLASS_OS` with `VERIFY_NONE`.

Risks: this stressor deliberately expects many syscalls to fail, so regressions can be hidden unless failures are unexpected and logged. Some operations are rate-limited by static timestamps shared across descriptors. Socket-family availability, privileged raw sockets, namespace ioctls, and Linux-only interfaces make coverage very build- and runtime-dependent. Descriptor count `n` can be zero only if every opener fails, which would make random fd selection unsafe, though practical builds should at least supply the bad fd opener.

Test signals: build on Linux with maximal feature detection; run with `--fd-abuse 1 --timeout` and check the debug line reporting opener/exerciser counts. Watch for fd leaks, temp-dir leftovers, unexpected fatal syscall logs, and behavior under low `ulimit -n`, restricted raw socket permissions, and OOM-child restart paths.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fd-abuse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fd-fork.c -->
## sources/test-tools/stress-ng/stress-fd-fork.c

Purpose: implements `fd-fork`, which opens a large number of duplicate descriptors, repeatedly forks children, and stresses descriptor closing by normal `close()` loops or `close_range()`.

Important APIs/types/functions: `stress_fd_close_info_t` holds close metrics, close-range state, and min/max fd values. `stress_fd_files[]` maps `--fd-fork-file` choices to `/dev/null`, `/dev/random`, stdin, stdout, and `/dev/zero`. `stress_fd_close()` first attempts `shim_close_range(fd_min, fd_max, 0)` and falls back to closing the tracked fd array, updating nanosecond-per-close metrics. `stress_fd_fork()` owns option handling, descriptor duplication, fork fan-out, cleanup, and metric reporting.

Control flow: the stressor clamps `--fd-fork-fds` to `stress_fs_file_limit_get()`, mmaps the fd array and shared close-info state, opens the selected source fd, and then synchronizes. In each loop it duplicates the source fd in batches of 10000 until the requested or system limit is reached, forks up to eight children, optionally has children close the inherited descriptors, waits for them, and repeats while allowed.

State and persistence behavior: no filesystem state is created beyond opening the selected device or stdio fd. The mapped fd table persists across the stressor lifetime and is closed in `tidy_fds`; the close metrics are stored in the mapped info block and emitted before unmapping.

Dependencies and integration points: uses stress-ng mmap helpers, file-limit helper, fork/wait helpers, bogo and metrics APIs, and `shim_close_range`. It is registered as `CLASS_FILESYSTEM | CLASS_OS`, has `VERIFY_ALWAYS`, and exposes `fd-fork-fds` and `fd-fork-file` options.

Risks: high fd counts can exhaust process or system fd tables, memory, or fork capacity; the code handles this by reducing the effective fd count and exiting when no children can be forked. `close_range()` metrics count the full min/max range, not only fds that were definitely open. Child close behavior is random, so close-path coverage varies run to run.

Test signals: run with low and high `--fd-fork-fds`, each `--fd-fork-file` mode, and systems with/without `close_range()`. Confirm metrics for close latency, peak descriptors open, and seconds to open all descriptors appear, and verify no descriptors remain open after cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fd-fork.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fd-race.c -->
## sources/test-tools/stress-ng/stress-fd-race.c

Purpose: implements `fd-race`, a Linux pthread stressor that races file descriptor open, transfer, use, and close paths by passing fds over UNIX-domain sockets while threads concurrently operate on nearby descriptor numbers.

Important APIs/types/functions: `stress_fd_race_filename_t` stores candidate filenames and open flags. `stress_fd_race_context` shares args, fd arrays, max fd limit, socket port, device ids, pthread barrier, and the currently opening fd. `stress_race_fd_send()` and `stress_race_fd_recv()` send and receive descriptors with `SCM_RIGHTS`. `stress_fd_race_close_fds()` closes by `close_range()` or several ordered/random loops. `stress_fd_race_current()` races `dup`, `fstat`, syncs, `lseek`, `fcntl`, `flock`, `ioctl(FIONREAD)`, poll, and select against descriptors around `current_fd`.

Control flow: the main stressor creates a temp file, optionally scans top-level `/dev` and `/proc`, reserves a per-instance local socket port, allocates the fd array, initializes a pthread barrier, and forks. The child runs `stress_race_fd_client()`, connecting to the server, receiving up to `max_fd` descriptors, spawning four pthreads that write to received regular files when safe, then closing the fd set. The parent runs `stress_race_fd_server()`, accepting clients, repeatedly opening files from the list, publishing each fd with `sendmsg`, and closing the set while helper threads race current descriptor numbers.

State and persistence behavior: creates a temporary directory and file, builds a malloced filename list, reserves a socket address, and allocates fd storage. The UNIX socket path and temp file are unlinked in cleanup. Runtime state is intentionally shared across threads through `current_fd` and the fd array to provoke races.

Dependencies and integration points: compiled only on Linux with pthread and pthread barriers. It uses stress-ng networking helpers for socket addresses and port reservation, signal handling, scheduler application, OOM adjustment, temp files, and close-range shims. Registered as `CLASS_OS`, `VERIFY_ALWAYS`.

Risks: it intentionally pushes fd limits and ancillary-data send limits; expected transient errors include `EAGAIN`, `EINTR`, `ECONNRESET`, `ENOMEM`, `ETOOMANYREFS`, and `EPIPE`. Running as root is capped to keep fd headroom. Optional `/dev` probing avoids `/dev/watchdog` and numbered tty-like devices, but device side effects remain an environment risk.

Test signals: exercise default, `--fd-race-dev`, and `--fd-race-proc`; check skip paths when socket bind or pthread barrier setup fails. Watch for leaked UNIX socket paths, failed descriptor passing, unexpected sendmsg errors, and stability under low fd limits and high instance counts.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fd-race.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fibsearch.c -->
## sources/test-tools/stress-ng/stress-fibsearch.c

Purpose: implements `fibsearch`, a CPU/cache/memory search stressor that repeatedly searches a sorted `int32_t` array with a local Fibonacci-search implementation.

Important APIs/types/functions: `fibsearch()` is a generic `bsearch`-like routine taking key, base, member count, element size, and comparator. It computes the smallest Fibonacci number covering the array, narrows the range by comparing at Fibonacci offsets, and returns a matching pointer or `NULL`. `stress_fibsearch()` allocates and initializes the data, invokes `stress_sort_data_int32_init()`, counts comparisons through `stress_sort_compare_get()`, and emits comparison metrics.

Control flow: the stressor reads `--fibsearch-size`, applies minimize/maximize defaults, rounds allocation up to a multiple of eight elements, mmaps the array, synchronizes, and loops. Each iteration fills sorted data, resets comparison counters, searches for every element in the array, optionally verifies the returned pointer value, updates duration/comparison/item counters, and increments bogo operations.

State and persistence behavior: all state is in one anonymous private mapping plus local metric accumulators. No files or durable state are created. The mapping is named `fibsearch-data` and unmapped on exit.

Dependencies and integration points: depends on `core-mmap`, `core-shim`, and `core-sort` helper comparators/counters. Registered as `CLASS_CPU_CACHE | CLASS_CPU | CLASS_MEMORY | CLASS_SEARCH`, with optional verification and `fibsearch-size` option.

Risks: the final single-element check compares `key` to `ptr`, unlike the main loop's `ptr` to `key`; this is harmless for equality with the integer comparator but worth preserving in comparator-sensitive refactors. Large `--fibsearch-size` values can consume significant memory and time because every item is searched each iteration.

Test signals: run with minimum, default, and maximum sizes; enable `--verify` to catch search failures; confirm both "comparisons per sec" and "comparisons per item" metrics change with array size and no mmap skip occurs unexpectedly.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fibsearch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fiemap.c -->
## sources/test-tools/stress-ng/stress-fiemap.c

Purpose: implements `fiemap`, which stresses the Linux `FS_IOC_FIEMAP` ioctl while another process mutates file extents by writing sparse data and punching holes.

Important APIs/types/functions: `stress_fiemap_writer()` writes one-byte records at random 8 KiB-aligned offsets and optionally punches 8 KiB holes with `FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE`. `stress_fiemap_ioctl()` first asks the kernel for mapped extent count, reallocates a `struct fiemap` large enough for those extents, and issues a second ioctl to fetch them. `stress_fiemap_spawn()` forks ioctl workers synchronized with the parent. A global `counter_lock` serializes bogo counter updates across processes.

Control flow: `stress_fiemap()` creates a temp file, unlinks it after open, checks FIEMAP support, spawns up to four ioctl child processes sharing the same fd, synchronizes all workers, then runs the writer loop in the parent. On exit it sends SIGALRM to children, closes the fd, removes the temp dir, unmaps pid storage, and destroys the counter lock.

State and persistence behavior: a temporary sparse file exists only by fd after unlink. Extent mutations persist only for the stressor lifetime. Shared process state is limited to the inherited fd, mapped pid table, and named lock.

Dependencies and integration points: requires `linux/fs.h`, `linux/fiemap.h`, and `FS_IOC_FIEMAP`; otherwise registers unimplemented. Uses stress-ng temp-file, sync-start, kill/wait, file-usage, lock, random, and bogo-lock helpers. Registered as `CLASS_FILESYSTEM | CLASS_OS`, `VERIFY_ALWAYS`.

Risks: filesystem support varies; `EOPNOTSUPP` is a skip/not-implemented condition. Extent counts can change between the count and fetch ioctls due to the writer, intentionally exercising races. `O_SYNC` changes fdatasync behavior. ENOSPC and EOPNOTSUPP hole-punch responses are handled but reduce mutation coverage.

Test signals: run on ext4, xfs, btrfs, tmpfs, and filesystems without FIEMAP. Validate skip messages for unsupported filesystems, no realloc failures under heavy extent churn, and correct reaping of four child ioctl workers.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fiemap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fifo.c -->
## sources/test-tools/stress-ng/stress-fifo.c

Purpose: implements `fifo`, a named-pipe I/O stressor with one writer and multiple reader child processes validating ordered fixed-size records through a FIFO.

Important APIs/types/functions: `fifo_spawn()` forks synchronized reader processes. `stress_fifo_reader()` opens the FIFO nonblocking, waits with `poll()` or `select()`, optionally probes queued bytes with `ioctl(FIONREAD)`, reads exactly `fifo_data_size` bytes, validates monotonic record numbers with wrap masking, and occasionally exercises invalid FIFO operations such as `lseek()` and `mmap()`. `stress_fifo()` creates the FIFO, spawns readers, writes records, and reports write rate.

Control flow: option handling selects `--fifo-readers` and `--fifo-data-size`, applying minimize/maximize defaults. The parent creates a temp directory and FIFO, starts reader children, synchronizes, opens the FIFO for writing, repeatedly writes an aligned buffer whose first `uint64_t` increments, updates metrics and bogo operations, then closes, kills readers, unlinks the FIFO, and removes the temp dir.

State and persistence behavior: creates one temporary FIFO path and a mapped pid table for reader management. Data state is transient in the FIFO and aligned buffers. Cleanup removes the FIFO and temp directory.

Dependencies and integration points: requires `mkfifo()` and `sys/select.h`; uses `poll()` when available. Integrates with stress-ng sync-start pid lists, kill/wait helpers, temp-file helpers, pathconf probes, and metrics. Registered as `CLASS_PIPE_IO | CLASS_OS | CLASS_SCHEDULER | CLASS_IPC`, `VERIFY_ALWAYS`.

Risks: nonblocking readers can observe partial or zero reads during shutdown or overload; code treats wrong-size reads as failure. The order check assumes a single writer and fixed-size records. `fifo_data_size` is capped to 4096, aligning with portable pipe atomicity assumptions.

Test signals: run with reader counts 1 and 64 and data sizes 8 and 4096. Check write-rate metric name includes the byte size, no "did not get buffer" failures occur, and FIFO cleanup succeeds after interrupted runs.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fifo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-file-ioctl.c -->
## sources/test-tools/stress-ng/stress-file-ioctl.c

Purpose: implements `file-ioctl`, a filesystem ioctl coverage stressor that creates temporary files and exercises generic, clone/dedupe, allocation, mapping, and filesystem-specific ioctl commands.

Important APIs/types/functions: `check_flag()` validates that `FIONBIO` and `FIOASYNC` actually toggle `O_NONBLOCK`/`O_ASYNC` as observed through `F_GETFL`. `stress_file_ioctl_fs_t` maps filesystem names to btrfs, ext, nilfs, reiserfs, and xfs probe functions. The Linux `shim_space_resv` structure backs reservation ioctls not always exposed by libc headers. `stress_file_ioctl()` is the main loop and tracks whether any ioctl was compiled in.

Control flow: the stressor creates and unlinks a 1 MiB temp file, detects filesystem type, optionally creates and unlinks a destination file for reflink/dedupe ioctls, preallocates and syncs the files, synchronizes, then loops over all compiled ioctl blocks. It exercises close-on-exec, nonblocking/async, size and block queries, reflink/range clone, dedupe, invalid fd queries, version/xattr, reserve/unreserve/zero range, FIBMAP, UUID/sysfs path, and filesystem-specific probes, incrementing bogo once per full pass.

State and persistence behavior: uses unlinked temp files held open by fd. No durable file remains after close and temp-dir removal. Some ioctls mutate file allocation and flags during the run.

Dependencies and integration points: uses Linux fs headers when available, stress-ng temp-file helpers, filesystem info helpers, bad-fd helper, fallocate/fsync shims, and metrics-free bogo integration. Registered as `CLASS_FILESYSTEM | CLASS_OS`, `VERIFY_ALWAYS`.

Risks: ioctl availability is highly kernel/filesystem/header dependent; many calls are expected to fail. The ext4 UUID branch contains direct `write(1, "here\n", 5)` and `pr_inf("UUID...")`, which can pollute stdout/log output if compiled and supported. Freeze/thaw ioctls are intentionally disabled as fragile. Some checks validate side effects only when `F_GETFL` is available.

Test signals: run on ext4, xfs, btrfs, and filesystems without clone/dedupe support. Confirm no "no available file ioctls" skip on normal Linux builds, flag toggling checks pass, unsupported ioctls fail quietly, and stdout is inspected if EXT4_IOC_GETFSUUID is enabled.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-file-ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-filehole.c -->
## sources/test-tools/stress-ng/stress-filehole.c

Purpose: implements `filehole`, a sparse-file stressor that repeatedly writes, mmaps, zeroes, punches holes, probes holes/data with `lseek()`, and optionally defragments the file.

Important APIs/types/functions: `fallocate_modes[]` weights punching holes three-to-one over zero-range when available. `stress_filehole_write()` and `stress_filehole_read()` provide positioned I/O wrappers with expected transient-error handling. `stress_filehole_io()` writes a page, validates mmap visibility, modifies the mmap, applies a random fallocate mode, optionally verifies zeroed data, writes neighboring data, and applies a second zero/hole operation. `stress_filehole_lseek_read()` samples `SEEK_SET`, `SEEK_DATA`, and `SEEK_HOLE`; `stress_filehole_non_zeros_to_holes()` converts nonzero pages to holes; `stress_filehole_defrag()` rewrites the sparse file into a dense temporary copy and renames it.

Control flow: the stressor clamps `--filehole-bytes`, allocates two page-sized buffers, creates a temp file, synchronizes, and loops. Each pass clears or truncates the file, writes and fallocates in reverse order, random order, and forward order, gathers max size/block and extent metrics, does random hole/data reads, fills with random data, punches alternating gaps, optionally defragments, converts nonzero pages back to holes, and repeats.

State and persistence behavior: creates a temporary file path and page buffers. File contents, extents, blocks, and sparse layout are heavily mutated but removed on cleanup. Metrics preserve maximum file size, maximum blocks, and average extents per file for the run.

Dependencies and integration points: compiled only with `fallocate()` plus punch-hole or zero-range support. Uses stress-ng mmap, madvise, fs extent, temp-file, fadvise, and metrics helpers. Registered as `CLASS_FILESYSTEM | CLASS_OS`, optional verification.

Risks: sparse behavior is filesystem-specific. ENOSPC/EFBIG/EAGAIN/EINTR are skipped, while other I/O errors fail. The fallback branch in `stress_filehole_non_zeros_to_holes()` contains unreachable typo-like references hidden by compile guards, so feature macro changes should be cautious. Defrag rename failure is nonfatal and silently keeps the original file.

Test signals: run with and without `--verify`, with minimum and large `--filehole-bytes`, and with `--filehole-defrag`. Confirm extents/block metrics are emitted, zero verification does not fail on punch/zero modes, and cleanup removes both original and `-tmp` files.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-filehole.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-filename.c -->
## sources/test-tools/stress-ng/stress-filename.c

Purpose: implements `filename`, a filename length/character-set stressor that probes or selects allowable filename bytes and repeatedly creates, stats, readdir-validates, and unlinks names of boundary and random lengths.

Important APIs/types/functions: `filename_opts[]` selects probe, POSIX, ext, UTF-8, and UTF-8-like modes. `allowed[256]` stores allowed byte values. `stress_filename_probe_length()` discovers effective max filename length; `stress_filename_probe()` discovers usable bytes by trying `creat()`. `stress_filename_generate_*()` creates repeated, random, valid UTF-8, or deliberately UTF-8-like names. `stress_filename_readdir()` verifies directory enumeration returns exactly the created file and checks stat identity. `stress_filename_test_normal()` and `_utf8()` perform create/stat/fdinfo/unlink checks.

Control flow: the parent creates a temp directory, reads `statvfs().f_namemax`, probes max length and allowed chars, synchronizes, then forks a worker child. The child loops through single-byte, max length, max-1, max+1 expected-fail, increasing length, and random length cases, alternating deterministic and random generated names, while periodically probing `pathconf()`. The parent waits, handles possible OOM SIGKILL restart policy, and tidies the directory.

State and persistence behavior: uses one temporary directory and transient test files. The global `allowed` table is process-local. Cleanup enumerates and unlinks residual entries before removing the directory.

Dependencies and integration points: uses stress-ng temp-dir, fdinfo, OOM adjustment, signal, scheduler, stat wrappers, filename-dot helpers, and option parsing. Registered as `CLASS_FILESYSTEM | CLASS_OS`, `VERIFY_ALWAYS`.

Risks: filename validity differs by filesystem, OS, locale, encoding translation, and compatibility layers. UTF-8-like mode intentionally generates invalid byte sequences. `stress_filename_probe()` has a complex errno condition that may not classify every platform's invalid-name errors cleanly. Readdir name mismatch is informational when stat identity proves the same file, acknowledging non-bijective filename encodings.

Test signals: run all `--filename-opts` modes on ext4, tmpfs, btrfs, Cygwin/WSL-like environments, and macOS if available. Watch for max-length discovery failures, residual files in the temp directory, and expected `ENAMETOOLONG` behavior for max+1 names.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-filename.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-filerace.c -->
## sources/test-tools/stress-ng/stress-filerace.c

Purpose: implements `filerace`, a multi-process shared-directory stressor that races many file, directory, metadata, allocation, locking, ACL, and lookup operations against a small evolving filename set.

Important APIs/types/functions: `stress_filerace_fops[]` is the central operation table, spanning stat/lseek/sync/read/write/pread/pwrite/fallocate/truncate/time updates/flock/FIBMAP/fadvise/fallocate/open/statx/readlink/openmany/leases/lockf/OFD locks/chdir/mmap/rw hints/ACL/access/name_to_handle/sendfile. `stress_filerace_file()` selects a random operation mix on odd seconds and a uniform operation on even seconds. `stress_filerace_filename()` maps elapsed time to two-digit hex names, slowly widening the collision set. `stress_filerace_child()` performs high-level create, unlink, open, rename, directory, link/symlink, mkdir, mass-open, and getdents actions while keeping up to 128 fds open.

Control flow: `stress_filerace()` records uid/gid and start time, installs SIGIO handling, creates a temp directory, forks `--filerace-procs` children, and runs the same child loop in the parent. Each child repeatedly chooses one of eleven directory/file scenarios, calls lower-level fops on opened fds, occasionally forks again while closing a full fd batch, and parent-side iterations increment bogo operations. Cleanup kills children and removes files/directories left in the temp path.

State and persistence behavior: global uid/gid/t_start guide ownership and filename selection. The stressor creates a temporary directory containing a bounded but constantly changing set of files, directories, and symlinks. It may mutate permissions, ownership, ACLs, extents, file size, locks, and timestamps; cleanup removes residual entries.

Dependencies and integration points: feature coverage depends on Linux fs headers, ACL libraries, sendfile, lock APIs, fallocate flags, statx/name_to_handle, and mmap/msync support. Integrates with stress-ng temp dirs, OOM includes, kill/wait helpers, random helpers, usage reporting, and signal handling. Registered as `CLASS_FILESYSTEM | CLASS_OS`, `VERIFY_NONE`.

Risks: this stressor intentionally creates races and ignores many expected errors, so it is useful for kernel/filesystem robustness rather than deterministic correctness. ACL and ownership operations may fail without privileges or filesystem support. The mmap operation installs temporary SIGBUS/SIGSEGV handlers because concurrent truncation/hole punching can invalidate mappings. One branch checks `if (tmp_fd != 1)` before closing, likely intending `!= -1`, which can leak fd 1 semantics or skip close if fd 1 is returned.

Test signals: run with `--filerace-procs` at 1, default, and 64 on filesystems with and without ACL/fallocate/statx support. Check for lingering temp entries, unexpected signal deaths, fd leaks, and stability under concurrent instances.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-filerace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-flipflop.c -->
## sources/test-tools/stress-ng/stress-flipflop.c

Purpose: implements `flipflop`, a scheduler/cacheline contention stressor where paired pthread groups repeatedly clear and set individual bits in shared words using compare-and-swap, optionally pinned to separate CPU sets.

Important APIs/types/functions: `stress_flipflop_info_t` describes one bit worker, including target word, masks, loop counters, CPU set, thread, parent pid, and shared hold/exit flags. `stress_flipflop_worker_t` pads each worker to a 64-byte boundary. `stress_flipflop_worker()` applies `sched_setaffinity()`, waits for release, repeatedly computes the target bit state, performs `__sync_val_compare_and_swap`, and records loops/tries/successes. `stress_flipflop_create_workers()` initializes one clear or set worker per bit.

Control flow: `stress_flipflop()` chooses bit count and optional tasksets, allocates distribution, bit, and worker arrays, synchronizes, creates clear workers on CPU set A and set workers on CPU set B, releases the hold flag, and pauses until SIGUSR1/SIGALRM wakes it. It aggregates worker loop counts into stress-ng bogo operations, exits when max ops or stop condition is reached, joins threads, and prints loop/try/success and percentile QPS summaries for instance zero.

State and persistence behavior: state is in anonymous memory: shared bit words, per-worker counters, and boolean control flags. No filesystem or durable state is created.

Dependencies and integration points: requires pthreads, `cpu_set_t`, `sched_setaffinity()`, and GCC-style `__sync_val_compare_and_swap`; otherwise registers unimplemented. Uses stress-ng affinity parsing, mmap population, sort, signal ignore handling, timing, and bogo APIs. Registered as `CLASS_SCHEDULER | CLASS_OS | CLASS_HOT`, `VERIFY_NONE`.

Risks: `stress_flipflop_uint64_cmp()` returns `-1` for both less-than and greater-than, which does not implement a correct total order for qsort and can skew percentile reporting. Division in informational percentages assumes nonzero loops/tries. Very high bit counts create two threads per bit, up to 131072 threads at the configured maximum, which may exceed system limits.

Test signals: run small bit counts, CPU-pinned tasksets, and maximize mode. Verify thread creation failures are handled, bogo counts progress, SIGUSR1 wakeups occur, and percentile output remains sane after fixing or testing the comparator behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-flipflop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-flock.c -->
## sources/test-tools/stress-ng/stress-flock.c

Purpose: implements `flock`, a multi-process stressor for BSD file-lock operations on a single shared temporary file.

Important APIs/types/functions: `stress_flock_child()` opens the shared file twice and loops through exclusive locks, nonblocking exclusive locks, shared locks, nonblocking shared locks, invalid lock combinations, invalid fd calls, and `/proc/locks` cache discard on Linux. It measures lock and unlock latency when called by the parent. `stress_flock()` creates the file, forks three synchronized child stressors, runs the same child routine in the parent with metrics enabled, then reaps children.

Control flow: the parent allocates a synchronized pid table, creates a temp file, forks `MAX_FLOCK_STRESSORS` children, sync-starts all workers, and enters the lock loop. The child routine checks that taking an exclusive lock on one fd prevents `LOCK_EX | LOCK_NB` on the second fd, unlocks, exercises invalid fd and invalid operation paths, and increments bogo operations for successful lock cycles until stopped.

State and persistence behavior: creates one temporary file and removes it plus the temp directory on deinit. Runtime state consists of two open read-only fds per process and local timing counters.

Dependencies and integration points: requires `flock()`, `LOCK_EX`, and `LOCK_UN`; shared/nonblocking paths are conditional. Uses stress-ng temp-file, sync pid, kill/wait, bad-fd, metric, and Linux `stress_fs_discard()` helpers. Registered as `CLASS_FILESYSTEM | CLASS_OS`, `VERIFY_ALWAYS`.

Risks: lock semantics differ across filesystems and network mounts. The invalid `LOCK_EX | LOCK_SH` combination may be accepted on some kernels or treated differently, so failure expectations should be platform-aware. Opening files read-only while testing locks is fine for flock but may interact with unusual filesystem policies.

Test signals: run on local ext4/xfs/tmpfs and network filesystems if available. Confirm no unexpected double-lock success, metrics for nanoseconds per lock/unlock are emitted, children are SIGALRM reaped, and temp files do not remain.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-flock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-flushcache.c -->
## sources/test-tools/stress-ng/stress-flushcache.c

Purpose: implements `flushcache`, a CPU cache stressor that flushes or demotes data-cache lines and modifies executable code pages to force instruction-cache maintenance.

Important APIs/types/functions: `stress_flushcache_context_t` holds i-cache function pointer, data and instruction mappings, sizes, line sizes, and x86 feature flags. `clear_cache_page()`, `dcbst_page()`, `cldemote_page()`, and `clflush_page()` provide architecture-specific line operations. `stress_flush_icache()` makes the instruction mapping writable/executable, toggles bytes, calls `shim_flush_icache`, PPC `icbi`, compiler clear-cache, and `shim_cacheflush`, restores RX permissions, and executes the generated return stub. `stress_flush_dcache()` walks data pages and applies x86/PPC flushes plus `shim_cacheflush`.

Control flow: `stress_flushcache()` discovers LLC/data and L1 instruction cache sizes, applies user byte overrides, clamps to page size, accounts for NUMA node scaling, maps an executable instruction-cache page, copies `stress_ret_opcode` into it, and runs `stress_flushcache_child()` through the OOM-child wrapper. The child maps the data buffer, disables huge pages where possible, synchronizes, and loops over instruction and data flushes until stopped.

State and persistence behavior: all state is anonymous memory. The instruction mapping is shared and executable; the data mapping is shared in the child and unmapped on exit. No files are created.

Dependencies and integration points: build requires supported architectures, `mprotect()`, compiler support, and architecture cacheflush/return-stub support. Integrates with core arch asm helpers, cache-size discovery, NUMA helpers, mmap/OOM wrappers, and the stressor `supported` hook `stress_asm_ret_supported`. Registered as `CLASS_CPU_CACHE`.

Risks: executable writable mappings and cache instructions are architecture-sensitive and can fail under W^X policies, seccomp, or unusual kernels. Help text has misspelled option labels `flushcashe-*` while opts use `flushcache-*`. The instruction flush loop uses data cache line size for stepping through i-cache bytes, which is probably intentional fallback but should be reviewed on split-line-size architectures.

Test signals: build/run on x86, ARM, RISC-V, s390, PPC/PPC64 where supported. Verify skip behavior when executable mmap or mprotect fails, perf cache-miss counters move, NUMA scaling message appears on multi-node systems, and both user byte options are honored.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-flushcache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fma.c -->
## sources/test-tools/stress-ng/stress-fma.c

Purpose: implements `fma`, a floating-point compute stressor that repeatedly applies multiply-add and multiply-subtract patterns to aligned float and double arrays, optionally using libc `fma()`/`fmaf()` shims.

Important APIs/types/functions: `stress_fma_t` stores aligned initial, working, and verification arrays for 512 doubles and floats plus scalar operands. `stress_fma_funcs[]` contains hand-written add/sub variants for 132, 213, and 231 operand orderings in double and float forms. When available, `stress_fma_libc_funcs[]` mirrors those operations through `shim_fma()` and `shim_fmaf()`. `stress_fma_init()` fills random initial values; `stress_fma_reset_a()` restores both working copies.

Control flow: `stress_fma()` selects libc or non-libc function arrays, catches SIGILL, mmaps the state object, initializes data after sync, and loops. Each iteration resets arrays, advances operand indices, runs six functions from either the add or subtract half of the table, increments bogo, optionally repeats the same computations on the second copy and byte-compares float/double results, then flips the offset between the two halves.

State and persistence behavior: state is one anonymous private mapping named `fma-data`, marked mergeable. No durable state is created. Floating-point data mutates every iteration but is reset from the initial arrays before each operation set.

Dependencies and integration points: uses math headers, stress-ng target clones, pragma unroll helpers, mmap/madvise, put/shim utilities, and SIGILL handling for CPU feature safety. Registered as `CLASS_CPU | CLASS_FP | CLASS_COMPUTE`, with optional verification and `--fma-libc`.

Risks: exact byte comparison under `--verify` assumes deterministic results between identical runs in the same process and function path, not equivalence between libc and non-libc paths. Target-cloned code and fused operations may trigger SIGILL on misdetected CPU support, hence the signal guard. The optional `USE_FMA_FAST` macro is disabled, so `FP_FAST_FMA*` names are not used unless that macro changes.

Test signals: run default and `--fma-libc` builds with and without `--verify`, across CPUs with and without hardware FMA. Confirm SIGILL is caught rather than crashing, verification arrays remain identical, and fallback messaging appears when libc fma helpers are unavailable.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fma.c -->
