# Research: subset-b-009366

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-copy-file.c -->
# sources/test-tools/stress-ng/stress-copy-file.c

## Purpose
This stressor exercises Linux `copy_file_range()` behavior through stress-ng's filesystem workload framework. It creates a temporary source file and destination file, writes random data into source ranges, copies fixed-size chunks between randomized offsets, optionally verifies copied bytes, and records copy throughput. When the build lacks `copy_file_range()` support it registers an unimplemented stressor with the same option/help metadata.

## Important APIs, Types, And Functions
The exported object is `stress_copy_file_info`, classified as filesystem and OS work with optional verification. `opts` exposes `copy-file-bytes` with minimum, maximum, maximize, and minimize handling. `stress_copy_file_seek64()` wraps `lseek64()` or guarded `lseek()` fallback. `stress_copy_file_fill()` fills a file region with a repeated random byte. `stress_copy_file_range_verify()` compares source and destination windows in 4 KiB buffers. `stress_copy_file()` owns setup, the copy loop, error classification, metrics, and cleanup.

## Control Flow
`stress_copy_file()` normalizes the requested total bytes across instances, creates a temp directory, opens an unlinked original file and unlinked copy file, truncates the input, and queries optional `pathconf()` transfer parameters. After the sync barrier it repeatedly selects random source and destination offsets, writes `DEFAULT_COPY_FILE_SIZE` bytes to the input, times `shim_copy_file_range()`, verifies the copy when `--verify` is active, deliberately calls `copy_file_range()` with bad descriptors and flags, fsyncs the output, and increments bogo operations. `ENOSYS` and filesystem `EINVAL` are treated as skip/no-resource cases; ordinary failures are reported.

## State And Persistence
State is local to the worker except for stress-ng global options, metrics, temporary filesystem space, and process state markers. Files are unlinked soon after opening, so the persistent artifact is temporary storage pressure rather than durable names. Metrics record harmonic-mean MB/s based on successful copied bytes and measured syscall duration.

## Dependencies And Integration Points
This file depends on stress-ng filesystem helpers, random MWC generators, shim syscall wrappers, bogo/metrics APIs, and compile-time `HAVE_COPY_FILE_RANGE`. It integrates with the option parser through `OPT_copy_file_bytes` and with the global verify/minimize/maximize flags.

## Risks
Large `copy-file-bytes` values can consume substantial temporary filesystem capacity across instances. Filesystems differ in `copy_file_range()` support, so `EINVAL` may indicate unsupported kernel splice paths rather than a test failure. Verification only checks the copied window and relies on correct offset restoration. The fallback seek path must reject offsets too large for `off_t` to avoid truncation.

## Test Signals
Useful signals are successful runs on filesystems with native copy support, graceful `EXIT_NO_RESOURCE` on unsupported kernels/filesystems, accurate verify-mode comparisons, cleanup of temporary directories, and a nonzero "MB per sec copy rate" metric. Fault paths should cover `ENOSPC`, bad descriptor calls, bad flag calls, and per-instance byte scaling.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-copy-file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-cpu-online.c -->
# sources/test-tools/stress-ng/stress-cpu-online.c

## Purpose
This Linux-only stressor repeatedly takes CPUs offline and online through sysfs to exercise CPU hotplug, scheduler affinity, and kernel CPU-online state transitions. It requires root privileges and advertises options for trying CPU affinity during hotplug and for including CPU 0.

## Important APIs, Types, And Functions
The exported object is `stress_cpu_online_info`, classified as CPU, OS, and pathological work. `stress_cpu_online_supported()` checks root and writable `/sys/devices/system/cpu/cpu1/online`. `stress_cpu_online_set()` writes `"0\n"` or `"1\n"` to a CPU online file and classifies transient errors as no-resource. `stress_cpu_online_get()` reads online state. `stress_cpu_online_set_affinity()` optionally pins the caller to a target CPU. `stress_cpu_online()` contains CPU discovery, child affinity helper setup, hotplug loop, cleanup, and metrics.

## Control Flow
The stressor reads `cpu-online-affinity` and `cpu-online-all`, verifies root, bounds configured CPUs to 65536, and builds a boolean map of CPUs with readable/writable `online` control files. A helper child may be forked; the parent writes upcoming CPU ids through a pipe and the child repeatedly tries to set its affinity to CPUs being offlined. The parent then selects CPUs sequentially, reverse sequentially, or randomly depending on instance number, skips CPU 0 unless requested, checks current online state, optionally pins itself, writes offline, verifies state, writes online, verifies state, updates timing counters, and yields.

## State And Persistence
The only durable external state is sysfs CPU online status, and the stressor explicitly restores all controllable CPUs online before exit. In-process state includes the CPU capability map, child pid/pipe, previous CPU selection, and timing counters. Metrics report milliseconds per offline and online action.

## Dependencies And Integration Points
This file depends on Linux sysfs CPU hotplug files, scheduler affinity APIs, stress-ng process state/sync/metrics helpers, root privileges, and `core-killpid` cleanup. It integrates with option parsing through `OPT_cpu_online_affinity` and `OPT_cpu_online_all`.

## Risks
CPU hotplug is disruptive and can destabilize workloads, trigger kernel/driver bugs, or interact badly with cpuset and affinity policy. Running multiple instances disables `--cpu-online-all` to reduce CPU 0 risk, but other CPUs can still be critical to the host. Failures such as `EBUSY` and `EOPNOTSUPP` are expected on some systems. Cleanup must run to restore all CPUs online and kill the helper child.

## Test Signals
Signals include skip behavior for non-root or unwritable sysfs, correct restoration of online state after interruption, timing metrics, absence of leaked helper processes, and successful operation with and without affinity mode. Kernel logs, scheduler warnings, and CPU hotplug tracepoints are important external validation.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-cpu-online.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-cpu-sched.c -->
# sources/test-tools/stress-ng/stress-cpu-sched.c

## Purpose
This stressor aggressively exercises scheduler, affinity, priority, process, timer, and optional NUMA policy paths. It creates many child processes per worker, repeatedly changes their CPU affinity and scheduling policy, sends stop/continue signals, forks and execs short-lived children, and gathers scheduler-related side effects through `/proc` and debugfs reads.

## Important APIs, Types, And Functions
`stress_cpu_sched_info` exports the stressor when scheduling and `sched_setscheduler()` support exist. `stress_cpu_sched_nice()` adjusts priority and Linux autogroup. `stress_cpu_sched_setaffinity()` and `stress_cpu_sched_setscheduler()` are the core mutators, covering normal policies, reset-on-fork variants, realtime policies, and `SCHED_DEADLINE` through `shim_sched_setattr()`. `stress_cpu_sched_set_handler()` installs an optional realtime-timer signal handler that perturbs scheduling from `SIGRTMIN`. `stress_cpu_sched_fork()` and `stress_cpu_sched_exec()` exercise fork/exec paths. `stress_cpu_sched_child()` owns child creation and the parent control loop.

## Control Flow
`stress_cpu_sched()` discovers affinity-capable CPUs, allocates optional NUMA masks, lowers OOM priority, synchronizes, and runs `stress_cpu_sched_child()` through `stress_oomable_child()`. The child reads `cpu-sched-procs`, creates up to 1024 children, and each child loops through yields, nanosleeps, priority changes, `getcpu()`, nop loops, optional `set_mempolicy()`, and random affinity changes until timeout or stop. The controller shuffles pid order, optionally `SIGSTOP`s each child, changes affinity and scheduler policy, resumes it, updates priority, pulses extra stop/continue signals, periodically probes load/rusage/scheduler files, occasionally forks an exercising subprocess, and occasionally execs stress-ng with `--exec-exit`.

## State And Persistence
Global static state includes the child pid array, discovered CPU list, optional POSIX timer id, and optional NUMA mask. Per-run state is mostly process-tree and kernel scheduler state; it is not intended to persist beyond the stressor. Child pids are killed on exit through `stress_kill_and_wait_many()`, and affinity CPU memory/NUMA masks are freed.

## Dependencies And Integration Points
Dependencies include Linux/POSIX scheduling APIs, affinity helpers, capability checks, realtime timer APIs, signal handling, process kill helpers, NUMA helpers, OOM wrappers, load/rusage shims, `/proc/pressure/*`, `/proc/schedstat`, and `/sys/kernel/debug/sched/debug`. The stressor is classified as scheduler and OS work and exposes `cpu-sched-procs`.

## Risks
This code intentionally exercises privileged and error-heavy paths; realtime/deadline policy changes can fail or affect host responsiveness, and high process counts can exhaust pids or memory. The hrtimer signal handler calls limited stress-ng helpers while preserving `errno`; any unsafe expansion would be risky. NUMA policy and scheduler command availability vary by kernel. Correct cleanup of stopped children is essential, otherwise children could remain paused or running.

## Test Signals
Run with low and high `cpu-sched-procs`, with and without `CAP_SYS_NICE`, across kernels with different policy sets. Signals include no leaked child processes, no stuck `SIGSTOP` children, graceful fallback for unsupported realtime/deadline features, bogo progress, and scheduler/debugfs/proc probes not causing hard failures. Lockdep, scheduler tracepoints, and OOM handling are useful external signals.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-cpu-sched.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-cpu.c -->
# sources/test-tools/stress-ng/stress-cpu.c

## Purpose
This is stress-ng's general CPU compute workload. It exposes many selectable CPU methods covering integer arithmetic, floating point, complex math, checksums, recursion, branch behavior, conversions, division, image-style dithering, matrix multiplication, primality, statistics, and mathematical constants. The default `all` method rotates across the method table to provide broad CPU coverage.

## Important APIs, Types, And Functions
`stress_cpu_method_info_t` maps method names to `stress_cpu_func` callbacks and normalization rates. The method table includes hand-written kernels such as `stress_cpu_sqrt()`, `stress_cpu_gcd()`, `stress_cpu_fft()`, `stress_cpu_matrix_prod()`, `stress_cpu_prime()`, `stress_cpu_stats()`, and many generated kernels produced by `STRESS_CPU_INT`, `STRESS_CPU_FP`, `STRESS_CPU_COMPLEX`, and `STRESS_CPU_INT_FP`. `stress_call_cpu_method()` dispatches one method and updates normalized bogo count. `stress_per_cpu_time()` selects process CPU time when available. `stress_cpu()` implements option handling, load throttling, dispatch, and cleanup.

## Control Flow
At startup `stress_cpu()` catches `SIGILL`, reads `cpu-load`, `cpu-load-slice`, `cpu-method`, and `cpu-old-metrics`, initializes per-method scale factors, waits at the sync barrier, and either sleeps for zero-load, spins at 100% load, or enters a throttled load loop. In full-load mode it disables FP subnormal handling, calls the selected method until stop or failure, then restores subnormal handling. In partial-load mode it runs a slice by fixed iteration count, random CPU-time window, or requested millisecond duration, computes the sleep delay needed to approximate the requested CPU percentage, sleeps with `select()` or nanosleep, and carries timing bias forward.

## State And Persistence
Most methods are stateless across calls except deliberate static buffers and accumulators, such as FFT buffers, matrix arrays, dither pixels, parity table, logistic map state, and LFSR state. Stress-ng global flags control verification and load settings. Metrics are bogo counts normalized by per-method rates unless `cpu-old-metrics` is requested. There is no external persistent state.

## Dependencies And Integration Points
This file depends heavily on stress-ng core math shims, random generators, bitops, network checksum helper, put helpers that prevent optimization, target-clone attributes, architecture feature macros, and the option parser. Compile-time feature checks include complex arithmetic, decimal and extended floating types, 128-bit integers, compiler builtins, and architecture exclusions such as S390 decimal math.

## Risks
Many verification checks rely on exact or tolerance-based numeric results that can vary with compiler, libc, architecture, floating mode, and optimization flags. Some generated mixed int/fp methods intentionally rely on overflow semantics for unsigned types; accidental signed conversions would be risky. The `all` dispatcher uses a static method index, so behavior is process-local and rotating. Load throttling is approximate and can be distorted by CPU affinity, scheduler noise, and wall-clock/CPU-clock mismatches.

## Test Signals
Key signals are successful method selection for every advertised `cpu-method`, verify-mode pass across supported architectures, stable partial-load behavior, no `SIGILL` from unsupported generated instructions, and sane normalized bogo counts. Targeted tests should exercise optional complex, decimal, float128, int128, and rand48 paths on platforms that expose them.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-cpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-crc.c -->
# sources/test-tools/stress-ng/stress-crc.c

## Purpose
This stressor exercises CRC calculations across 8-, 16-, 32-, and 64-bit widths, multiple data element widths, and normal versus reverse bit ordering. It also validates compiler CRC builtins against software fallback implementations by comparing fixed input data to endian-specific expected results.

## Important APIs, Types, And Functions
`stress_crc_func_t` is the common CRC callback signature, and `stress_crc_method_t` records function, print width, expected result, and method name. Implementations include `stress_crc_crc8_data8()`, `stress_crc_crc16_data8()`, `stress_crc_crc16_data16()`, CRC32 variants, optional CRC64 variants, and reverse CRC counterparts. Each function uses a compiler builtin when available or a bitwise polynomial fallback otherwise. `stress_crc()` drives execution, validation, per-method metrics, and total Mbit/s reporting.

## Control Flow
Static aligned test data is interpreted as bytes, 16-bit words, 32-bit words, or 64-bit words depending on method. `stress_crc()` zeroes a metrics array, waits for synchronization, then repeatedly runs every method for `CRC_LOOPS` iterations while the stressor should continue. A mismatch logs the method name, actual value, and expected value, marks failure, and stops the run. On completion it emits per-method operations-per-second metrics and aggregate CRC throughput.

## State And Persistence
State is limited to fixed input data, the compile-time method table, and per-run metrics. There is no external persistence. Expected values are selected separately for little-endian and non-little-endian builds, and 64-bit methods are compiled only when `ULONG_MAX` indicates a 64-bit platform.

## Dependencies And Integration Points
The file depends on compiler-provided CRC builtins when present, stress-ng bit-reversal helpers for reverse CRC fallbacks, timing/metrics APIs, and architecture endian macros. It registers as CPU/compute work with `VERIFY_ALWAYS` and advertises enough metric slots for every method plus aggregate throughput.

## Risks
Expected results are sensitive to byte order, data packing, and builtin semantics. If a compiler builtin implements a different reflected/non-reflected convention than assumed, this stressor will surface it as a failure. Fallback loops step by element width and assume the fixed data length is compatible with every grouping. Per-method metrics are meaningful only when methods have nonzero duration.

## Test Signals
Signals include exact expected CRC values on little- and big-endian targets, correct inclusion/exclusion of 64-bit methods, matching behavior between builtins and fallbacks, and nonzero per-method and aggregate metrics. Build-matrix testing with and without each `HAVE_BUILTIN_*` macro is especially valuable.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-crc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-crypt.c -->
# sources/test-tools/stress-ng/stress-crypt.c

## Purpose
This stressor exercises libc/libcrypt password hashing methods. It generates random salts and phrases, runs `crypt_r()` or `crypt()` for either all supported method prefixes or one selected method, tolerates unsupported algorithms, and reports per-method encryptions per second.

## Important APIs, Types, And Functions
`crypt_method_t` maps a salt prefix to a human-readable method name. `crypt_methods` includes all, bcrypt, bsdicrypt, descrypt, gost-yescrypt, MD5, NT, scrypt, SHA-1, SHA-256, SHA-512, SunMD5, and yescrypt prefixes. `stress_crypt_method()` exposes method names to option parsing. `stress_crypt_id()` times one encryption and handles unsupported `crypt` errors. `stress_crypt()` allocates metric storage, generates input strings, calls methods, updates bogo count, and emits metrics.

## Control Flow
The stressor reads `crypt-method`, allocates a metrics array, initializes `crypt_data` when using `crypt_r()`, and waits for the sync barrier. Each loop creates a random setting and phrase from the 64-character crypt alphabet. In `all` mode it iterates every method after index 0, splices the method prefix into the setting, resets `crypt_data.initialized`, and calls `stress_crypt_id()`. In single-method mode it builds one setting and calls only the selected method. Fatal unexpected crypt errors stop the loop; unsupported or invalid methods are ignored.

## State And Persistence
State is in-memory only: current phrase, current setting, optional static `struct crypt_data`, and per-method timing/count metrics. No password hashes are stored persistently. The output metrics are reported for methods that produced at least one successful result.

## Dependencies And Integration Points
The stressor is compiled only with libcrypt and either `crypt.h` or FreeBSD support. It depends on stress-ng settings, random number generation, metric helpers, and memory allocation. The method selector is wired through `OPT_crypt_method`.

## Risks
Method availability depends on libcrypt implementation and system policy, so `EINVAL`, `ENOENT`, `ENOSYS`, and `EOPNOTSUPP` are normal. Some methods can be intentionally expensive and dominate runtime. Non-`crypt_r()` builds use process-global `crypt()` state, which is less thread-safe in general, although stress-ng workers are process-based. The single-method branch uses the selected index; option parsing must keep it in range.

## Test Signals
Builds without libcrypt should register the unimplemented reason. Runtime signals include successful metrics for available methods, graceful silence for unavailable methods, bogo increments on successful encryptions, and no fatal failure for expected unsupported-algorithm errors. Testing should cover both all-method and selected-method modes.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-crypt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-ctrig.c -->
# sources/test-tools/stress-ng/stress-ctrig.c

## Purpose
This stressor exercises C complex trigonometric functions for `cos`, `sin`, and `tan` across float, double, and long-double variants when the platform exposes them. It accumulates deterministic sums over a fixed complex path and verifies the results against precomputed tolerances.

## Important APIs, Types, And Functions
`stress_ctrig_method_t` maps method names to boolean test callbacks. Methods include `stress_ctrig_ccos()`, `stress_ctrig_ccosf()`, `stress_ctrig_ccosl()`, `stress_ctrig_csin*()`, and `stress_ctrig_ctan*()` variants behind feature macros. `stress_ctrig_exercise()` times a method, updates metrics, and logs checksum failures. `stress_ctrig_all()` runs every concrete method. `stress_ctrig()` handles option selection, loop control, metrics, and process state.

## Control Flow
Each concrete method initializes a complex value at roughly `-0.5 + 0.5i`, steps it by a small complex delta for `STRESS_CTRIG_LOOPS`, accumulates the shim complex trig result, increments bogo count, and returns true if the accumulated checksum exceeds the method-specific tolerance. The top-level stressor reads `ctrig-method`, zeroes metrics, synchronizes, repeatedly calls the selected method, and fails the stressor on the first checksum mismatch.

## State And Persistence
State is limited to static expected sums, the method table, and per-method metrics. There is no external persistence. The `all` method uses nested metrics updates for concrete methods and reports rates for methods with observed durations.

## Dependencies And Integration Points
This file depends on `complex.h`, stress-ng complex shims, math library functions, target-clone and pragma helpers, and option parsing through `OPT_ctrig_method`. Without complex support it registers as unimplemented while preserving option metadata.

## Risks
Complex math results vary with libc accuracy, long-double representation, compiler optimization, and architecture, so tolerances are intentionally different for float/double/long-double. The methods are verify-always, making platform math regressions visible as stressor failures. Missing feature macros shrink the method table, so option indexes must come from the generated selector.

## Test Signals
Signals include all advertised methods passing checksum verification, per-method operations-per-second metrics, correct unimplemented behavior without `complex.h`, and stable tolerances on targets with 80-bit, 128-bit, or ordinary long-double formats.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-ctrig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-cyclic.c -->
# sources/test-tools/stress-ng/stress-cyclic.c

## Purpose
This stressor measures cyclic scheduling/timer latency under selectable sleep mechanisms and scheduler policies. It is both a benchmark and a scheduler stressor: it attempts realtime or other policies, gathers latency samples, reports summary statistics and percentiles, and can print latency distribution buckets.

## Important APIs, Types, And Functions
`stress_policy_t` describes scheduler policies and whether `CAP_SYS_NICE` is required. `stress_rt_stats_t` stores latency samples, min/max/mean/mode/stddev, priority bounds, and sample counts. Sleep methods include `stress_cyclic_clock_nanosleep()`, `stress_cyclic_posix_nanosleep()`, `stress_cyclic_poll()`, `stress_cyclic_pselect()`, `stress_cyclic_itimer()`, and `stress_cyclic_usleep()`. `stress_cyclic_stats()` records one latency. `stress_rt_stats()` sorts and summarizes samples. `stress_rt_dist()` prints histograms. `stress_cyclic()` is the main runner.

## Control Flow
Initialization maps a shared state object and creates a lock to throttle repeated scheduler error messages. `stress_cyclic()` reads distribution, method, policy, priority, sample count, and sleep interval options; validates method and policy availability; checks `CAP_SYS_NICE` for realtime policies; forces a default timeout if none was set; maps shared stats and latency arrays; computes scheduler priority bounds; and synchronizes. It forks a child so CPU and realtime limits can kill only the measurer. The child sets `RLIMIT_CPU` and optional `RLIMIT_RTTIME`, installs `SIGXCPU` handling, attempts the requested scheduler policy, then loops calling the selected cyclic method and incrementing bogo count until stop or timeout. The parent applies scheduler settings to itself, pauses, kills/waits for the child, then computes and prints statistics.

## State And Persistence
State is shared anonymous memory for global error count, runtime statistics, and latency samples. No external files are persisted. The report includes scheduler policy, optional sched-ext op name, requested delay, sample count, mean, mode, min, max, standard deviation, percentile samples, optional distribution, and a note if more sample storage was needed.

## Dependencies And Integration Points
Dependencies include POSIX clocks, timers, nanosleep, pselect/select availability, scheduler policy APIs, capability checks, rlimit handling, signal/longjmp helpers, shared mmap, stress-ng lock helpers, sorting, and process kill helpers. Options expose cyclic distribution, method, policy, priority, sleep duration, and sample count.

## Risks
Realtime policies can require privileges and can affect host scheduling. The child may be killed by CPU or realtime limits, so cleanup and parent reporting must tolerate partial samples. The `poll` method busy-waits and consumes CPU. Latency arrays can be large up to 100 million samples, so allocation failure must be handled. Percentile indexing assumes nonzero sample count and sorted samples. Scheduler support varies sharply by kernel, especially `SCHED_DEADLINE` and `SCHED_EXT`.

## Test Signals
Signals include skip behavior for missing policies or missing `CAP_SYS_NICE`, successful stats for every advertised method, correct fallback when `SCHED_DEADLINE` attr size is unsupported, bounded repeated scheduler error logging, distribution output when requested, and correct cleanup of mapped stats/latency regions. One-instance runs are the best benchmark signal; multi-instance runs are more useful for scheduler stress.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-cyclic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-daemon.c -->
# sources/test-tools/stress-ng/stress-daemon.c

## Purpose
This stressor repeatedly creates daemonized child processes to exercise `fork()`, `setsid()`, signal reset, environment clearing, descriptor rebinding, process reaping, capability dropping, and init/system reparenting behavior.

## Important APIs, Types, And Functions
`daemon_wait_pid()` optionally waits for a child when `daemon-wait` is enabled. `stress_make_daemon()` runs inside the first child, calls `setsid()`, closes standard descriptors, resets signals, clears the signal mask and optional environment, opens `/dev/null` as fds 0/1/2, then repeatedly forks daemon children. `stress_daemon()` owns the parent pipe, initial fork, result reads, bogo increments, and cleanup. `stress_daemon_info` exposes `daemon-wait`.

## Control Flow
The top-level worker disables `SIGALRM` stress-stop behavior, creates a pipe, synchronizes, and forks. The child closes the read side and calls `stress_make_daemon()`. That routine reports setup failures through the pipe before stdio closure, then the daemon child changes directory to `/`, clears umask, drops capabilities, marks run state, and writes success to the pipe. The original parent reads result codes, increments bogo count for successes, and either waits for the intermediate child or lets init reap descendants depending on `daemon-wait`.

## State And Persistence
The stressor intentionally manipulates process/session state but does not persist files. It may leave daemon children to be reaped by init when `daemon-wait` is false, by design. All communication to the original parent is through the pipe before descriptor cleanup.

## Dependencies And Integration Points
Dependencies include stress-ng signal helpers, capability dropping, fork retry helpers, process state APIs, `/dev/null`, optional `clearenv()`, and option parsing through `OPT_daemon_wait`. It is classified as scheduler and OS work.

## Risks
Fork pressure can hit pid or memory limits. Because stdout/stderr are intentionally closed in the daemon path, many later setup failures cannot be reported directly and are silently retried or cleaned up. Signal reset loops iterate over `MAX_SIGNUM`, which is platform-dependent. Incorrect `daemon-wait` use changes whether the stressor waits directly or relies on init reaping.

## Test Signals
Signals include successful bogo increments for daemon creations, no fd leaks around `/dev/null`, no zombie buildup when `daemon-wait` is enabled, acceptable init reaping when disabled, and graceful retry/backoff on `EAGAIN` or `ENOMEM` fork failures.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-daemon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-dccp.c -->
# sources/test-tools/stress-ng/stress-dccp.c

## Purpose
This stressor exercises Datagram Congestion Control Protocol socket I/O. It forks a client and server pair, binds a reserved port, accepts DCCP connections, sends variable-sized buffers using `send`, `sendmsg`, or optional `sendmmsg`, and measures message throughput.

## Important APIs, Types, And Functions
`stress_dccp_options()` exposes send mode names. `stress_dccp_client()` creates a DCCP socket, builds an interface/domain-specific address, retries connect, and receives until EOF or stop. `stress_dccp_server()` creates, binds, listens, accepts, sends message batches, probes socket state with `getsockname()`, `getsockopt(SO_SNDBUF)`, `getpeername()`, and optional `SIOCOUTQ`, then records throughput. `stress_dccp()` handles option parsing, interface validation, port reservation, fork, affinity, scheduling, and cleanup.

## Control Flow
The worker installs a SIGCHLD handler, reads interface, port, domain, send mode, and message-count options, validates the requested interface, reserves an instance-specific port, synchronizes, then forks. The child becomes the client, moves near the parent's CPU, applies scheduler settings, and receives data. The parent runs the server loop. The server accepts connections and sends up to `dccp-msgs` chunks per connection according to the selected method, incrementing bogo operations after send batches. On stop it closes sockets, reports messages per second, kills the client, and releases the port.

## State And Persistence
State is transient network/socket state plus a reserved port range in stress-ng's port manager. Optional AF_UNIX cleanup is present, though the domain mask defaults to IPv4/IPv6. No data is persisted beyond kernel socket buffers and metrics.

## Dependencies And Integration Points
The file depends on `SOCK_DCCP` and `IPPROTO_DCCP`, stress-ng network address/port/interface helpers, affinity and scheduler helpers, signal handling, kill helpers, and optional `sendmmsg()` and Linux socket ioctl support. Without DCCP definitions it registers an unimplemented stressor.

## Risks
DCCP is often disabled or unsupported by kernel configuration, so socket creation may skip as not implemented. Network namespace, firewall, or interface configuration can make connect/bind fail. The retry loop can delay failure by about one second. Send mode behavior differs by kernel, and large `dccp-msgs` values can hold a worker in connection I/O for a long time. Port reservation and release must remain paired.

## Test Signals
Signals include graceful skip on unsupported DCCP, successful loopback IPv4/IPv6 runs, correct interface fallback to loopback, port release after interruption, throughput metrics, and coverage of `send`, `sendmsg`, and `sendmmsg` where compiled.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-dccp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-dekker.c -->
# sources/test-tools/stress-ng/stress-dekker.c

## Purpose
This stressor validates and stresses Dekker-style mutual exclusion between two processes sharing memory. It uses volatile shared flags, a turn variable, explicit memory fences/barriers, and critical-section checks to expose weak memory ordering or broken barrier support.

## Important APIs, Types, And Functions
`dekker_mutex_t` stores `wants_to_enter[2]`, `turn`, and a shared `check` counter. `dekker_t` combines the mutex with cacheline-padded metrics for both participants. `stress_dekker_supported()` installs a temporary `SIGILL` handler and probes the architecture memory barrier. `stress_dekker_p0()` and `stress_dekker_p1()` implement the two halves of Dekker's algorithm. `stress_dekker()` maps shared memory, forks the peer process, runs both halves, combines metrics, and cleans up.

## Control Flow
The supported check uses `sigsetjmp()`/`siglongjmp()` to skip the stressor if the barrier instruction traps. Runtime maps a shared anonymous page, names it, zeros metrics, synchronizes, and forks. The child repeatedly enters participant 0's critical section, incrementing `check`; the parent repeatedly enters participant 1's critical section, decrementing `check` and incrementing bogo count. Both sides set their intent flag, fence/barrier, spin on the other flag and turn, enter the critical section, verify that the counter changed by exactly one, set the turn to the other participant, clear intent, and update timing metrics. Parent kills and waits for the child at exit.

## State And Persistence
State is one shared mmap region and a static pointer plus jump buffer. There is no filesystem persistence. The final metric is nanoseconds per mutex based on combined participant durations and counts.

## Dependencies And Integration Points
Dependencies include shim memory fences, optional ARM `dmb sy`, signal longjmp support, shared mmap, CPU affinity helper for the child, kill/wait helpers, and stress-ng metrics. If memory fencing or longjmp support is absent it registers as unimplemented.

## Risks
This is intentionally sensitive to memory ordering. Incorrect fence semantics can cause mutual exclusion failure and `check` mismatches. Spin loops can burn CPU and can run indefinitely if the peer dies without stop propagation. The fork-failure path should unmap shared memory; changes here should preserve cleanup. Cacheline padding assumes 64-byte intent to reduce metric contention.

## Test Signals
Signals include supported-probe skip on illegal barrier instructions, sustained bogo progress, zero mutex check failures, clean child termination, and plausible nanoseconds-per-mutex metrics. Running on weakly ordered architectures is the most valuable validation.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-dekker.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-dentry.c -->
# sources/test-tools/stress-ng/stress-dentry.c

## Purpose
This filesystem stressor thrashes directory entries by creating many files, probing existing and nonexistent names, performing miscellaneous directory operations, and unlinking files in selectable orders. It is designed to stress dentry cache, lookup failure paths, unlink ordering, and filesystem metadata operations.

## Important APIs, Types, And Functions
`stress_dentry_removal_t` maps order names to constants for forward, reverse, stride, and random removal. `stress_dentry_unlink_file()` removes one file and optionally verifies stored gray-code content first. `stress_dentry_unlink()` removes a full batch in the selected order. `stress_dentry_state()` reads Linux `/proc/sys/fs/dentry-state` for cache deltas. `stress_dentry_misc()` opens the temp directory and exercises `utime`, `fstat`, illegal reads/truncates/fallocate, mmap, futimens, select, locks, and fcntl. `stress_dentry()` is the main workload.

## Control Flow
The stressor reads `dentries` and `dentry-order`, creates a temporary directory, captures initial dentry count, and enters a loop. It creates files named from gray-coded values multiplied by two, optionally writes the gray code for verification, and increments bogo count. It then performs directory misc operations, syncs, probes existing files and generated nonexistent files, times bogus unlinks, increments an offset to avoid name reuse, unlinks the real files in forward/reverse/stride/random order, and repeats. On abort it computes dentry delta, emits timing metrics, force-unlinks remaining files, and removes the temp directory.

## State And Persistence
Persistent state is temporary files under the stress-ng temp directory until cleanup. Verify mode stores an 8-byte gray-code value in each file. Metrics track nanoseconds per file creation, existing access, bogus access, and bogus unlink. Linux dentry-state deltas are informational only.

## Dependencies And Integration Points
Dependencies include stress-ng temp-file helpers, prime helper for stride order, mmap helpers, optional file locking/select/utime/futimens/fallocate shims, Linux procfs for dentry stats, and global verify/maximize/minimize flags. Options are `dentries` and `dentry-order`.

## Risks
High dentry counts can exhaust filesystem space, inode limits, or directory performance. Verify mode adds reads and can fail if files were not written fully. Random order maps to one of the deterministic orders for each unlink batch, so it is not fully shuffled. `stress_dentry_misc()` intentionally calls invalid operations on directories; those should stay best-effort. Cleanup must remove files even after partial creation or `ENOSPC`.

## Test Signals
Signals include clean temp directory removal, no read verification errors, metrics for all four operation classes, correct handling of `ENOSPC`, and useful dentry allocation logs on Linux. Filesystem-specific testing should cover tmpfs, ext4/xfs, and constrained inode/free-space environments.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-dentry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-dev-shm.c -->
# sources/test-tools/stress-ng/stress-dev-shm.c

## Purpose
This Linux-only stressor exercises `/dev/shm` by creating an unlinked shared-memory-backed file, expanding it with `fallocate()`, mapping it, touching and verifying pages, applying random madvise behavior, and reporting mmap residency/dirty/swap statistics.

## Important APIs, Types, And Functions
`stress_dev_shm_context_t` stores the `/dev/shm` file descriptor and accumulated `stress_mmap_stats_t`. `stress_dev_shm_child()` performs truncate, rough maximum-size probing, mmap, page touch, verification, msync invalidation, and unmap work under an OOMable child. `stress_dev_shm()` validates `/dev/shm`, creates and unlinks the backing file, runs the child through `stress_oomable_child()`, reports mmap stats, closes the fd, and unmaps context.

## Control Flow
The top-level stressor maps a shared context, checks `/dev/shm` read/write availability, opens a unique file with `O_CREAT|O_EXCL|O_RDWR`, unlinks it, synchronizes, and starts an OOMable child. The child truncates the file to zero, uses an exponential/rough binary search with `shim_fallocate()` to find a large size, maps it private read/write, collects mapping stats, names and advises the mapping, writes one word per page using an address-derived value, verifies the same values, invalidates with `msync()`, unmaps, truncates to zero, and repeats.

## State And Persistence
The backing file is unlinked immediately, so storage pressure is transient and tied to the open fd. Shared context persists only for the worker lifetime. Reported state includes total, swapped, and dirtied mmap statistics accumulated from child observations.

## Dependencies And Integration Points
This file depends on Linux `/dev/shm`, stress-ng OOM child handling, madvise helpers, mmap stats helpers, random generators, file allocation/truncation shims, and stress-ng process state/metrics. Non-Linux builds register an unimplemented stressor.

## Risks
The workload can fill tmpfs and trigger `SIGBUS` or OOM pressure; the search deliberately avoids exact maximum sizing to reduce that risk. Private mappings mean writes fault private pages and may stress memory more than tmpfs persistence. Verification is page-stride based, not byte-for-byte. Cleanup must close the unlinked fd and unmap shared context on all paths.

## Test Signals
Signals include skip behavior when `/dev/shm` is missing or inaccessible, successful repeated allocation/map/verify cycles, no leaked named files, mmap stats output, and graceful OOM/no-resource behavior under small tmpfs limits.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-dev-shm.c -->
