# subset-b-009376 stress-ng source research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-nanosleep.c -->
# sources/test-tools/stress-ng/stress-nanosleep.c

## Purpose
`stress-nanosleep.c` implements the `nanosleep` stressor. It creates one or more pthreads that repeatedly issue very short `nanosleep(2)` calls, using fixed nanosecond, microsecond, millisecond, random, or CPU C-state-derived sleep durations. The stressor exercises timer interrupt delivery, high-resolution timer handling, scheduler wakeups, and optional cpuidle residency paths.

## Important APIs, Types, and Functions
The stressor is exported through `stress_nanosleep_info`, with `CLASS_INTERRUPT | CLASS_SCHEDULER | CLASS_OS`, `VERIFY_ALWAYS`, help text, and options for `nanosleep-threads` and `nanosleep-method`. `stress_nanosleep_method_t` maps option names to bit masks. `stress_ctxt_t` is the per-thread context: it carries `stress_args_t`, the cpuidle C-state list, local operation count, max operation quota, pthread handle, selected method mask, and optional overrun/underrun metric accumulators.

`stress_nanosleep_ns()` wraps `nanosleep()` and, when `clock_gettime(CLOCK_MONOTONIC)` is available, measures actual elapsed time against the requested interval. `stress_nanosleep_pthread()` runs the sleep loop for one worker thread. `stress_nanosleep()` is the stressor entry point, reading settings, allocating contexts, starting threads, aggregating counters, joining threads, and publishing sleep overrun metrics.

## Control Flow
The main stressor chooses the thread count from settings or min/max flags, divides the global bogo-op limit across threads, resolves the method mask, and optionally falls back from C-state mode to random sleeps when no cpuidle states are available. It installs a `SIGALRM` handler that sets the file-local `thread_terminate` flag, allocates `stress_ctxt_t` entries, and spawns threads.

Each thread loops while `stress_continue(args)` is true, `thread_terminate` is false, and its local max-op quota is not exceeded. C-state mode iterates the cpuidle list and sleeps for roughly `1000 * (residency + 1)` ns. Random mode tries a descending range of random sleep lengths. The fixed modes issue 1 ns, 1000 ns, and 1000000 ns sleeps. The parent enters sync wait, transitions to run state, periodically resets and sums per-thread counters into the shared bogo counter, then deinitializes on timeout or stop.

## State and Persistence
State is process-local and transient. `thread_terminate` and a global `sigset_t` are static file state. Per-thread counters and timing accumulators live in the allocated context array and are freed before return. Metrics are persisted only into stress-ng shared stats through `stress_metrics_set()`. No files or durable system state are changed.

## Dependencies and Integration Points
The implementation depends on `pthread_create`, `pthread_join`, `nanosleep`, `SIGALRM`, `clock_gettime`, stress-ng settings, logging, synchronization, bogo counters, and cpuidle helpers from `core-cpuidle.h`. It compiles to `stress_unimplemented` when pthread or nanosleep support is missing. It integrates with the global stress-ng lifecycle through `stress_proc_state_set`, `stress_sync_start_wait`, `stress_continue`, `stress_bogo_set`, and `stress_bogo_add`.

## Risks
The stressor can request up to 1024 threads, so resource exhaustion and `EAGAIN` from pthread creation are expected operating modes. The static `thread_terminate` flag is not reset at the start of `stress_nanosleep()`, so reuse in unusual in-process repeated invocations depends on process lifetime and prior state. Counter aggregation reads unsynchronized per-thread counters, acceptable for stress metrics but approximate. The underrun metric calculation appears suspicious: after subtracting overhead, it computes `(underrun_nsec / underrun_count) - underrun_nsec`, which likely subtracts the accumulated adjusted value rather than overhead. Very small sleep intervals make timing metrics highly scheduler and hardware dependent.

## Test Signals
Useful signals are successful build on both pthread and unimplemented paths, a short run such as `--nanosleep 1 --timeout 1 --metrics`, method parsing for `all`, `cstate`, `random`, `ns`, `us`, and `ms`, and runs with `--nanosleep-threads 1` and a larger thread count. On C-state-capable Linux systems, verify fallback messaging when C-states are unavailable and metrics emission for sleep overrun. Failure tests should include low thread limits to exercise the `EAGAIN` limited-thread path.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-nanosleep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-netdev.c -->
# sources/test-tools/stress-ng/stress-netdev.c

## Purpose
`stress-netdev.c` implements the `netdev` stressor, which repeatedly enumerates network interfaces and exercises Linux netdevice `ioctl(2)` queries. It is intended to cover interface configuration query paths and some invalid `SIOCGIFCONF` and `SIOCGIFNAME` cases without making persistent network configuration changes.

## Important APIs, Types, and Functions
The exported `stress_netdev_info` registers `stress_netdev()` as a `CLASS_NETWORK` stressor with always-on verification. The helper `stress_netdev_check()` centralizes ioctl error handling and treats common unsupported or permission-related errors as non-fatal. The `STRESS_NETDEV_CHECK` macro passes ioctl names into that helper for diagnostics. The stressor uses `struct ifconf`, `struct ifreq`, `socket(AF_INET, SOCK_DGRAM, 0)`, and many `SIOC*` netdevice commands guarded by compile-time feature macros.

## Control Flow
The stressor opens an IPv4 datagram socket, synchronizes with other workers, and enters a loop while the run continues and no fatal ioctl error has occurred. It first calls `SIOCGIFCONF` with a zeroed `ifconf` to discover the required buffer length, derives the interface count, allocates the buffer, and calls `SIOCGIFCONF` again to fill it. For each interface, it optionally checks the interface index, resolves names, validates returned index behavior, and queries flags, extended flags, address, netmask, metric, MTU, hardware address, hardware map, transmit queue length, destination address, broadcast address, memory, and link information where available. It also sends intentionally malformed `SIOCGIFCONF` lengths and random interface indexes to probe error paths. Each completed pass increments the bogo counter.

## State and Persistence
The only persistent kernel object is the transient socket, closed before return. Interface buffers are allocated and freed inside each loop iteration. The stressor does not set interface flags or addresses; mutation-oriented ioctls are present only in disabled `#if 0` blocks. It stores no durable state and reports failure state through the return code and stress-ng logging.

## Dependencies and Integration Points
This is Linux-specific and requires `SIOCGIFCONF`, `struct ifconf`, and `struct ifreq`. It includes `linux/sockios.h` and `net/if.h` where available. It uses stress-ng shims for memset, memory-free messages, logging, synchronization, process states, bogo counters, and random values. Unsupported builds export `stress_unimplemented` with an explanatory reason.

## Risks
The first `SIOCGIFCONF` call relies on platform behavior that returns the needed length when `ifc_buf` is null; that is Linux-oriented and guarded accordingly. Interface count is computed from `ifc_len / sizeof(struct ifreq)`, which is conventional for this ioctl but not a universal portable interface enumeration strategy. Network namespaces or systems with no interfaces cause skip-like behavior. The `SIOCGIFNAME` validation sets `ifr_ifindex = i`, but Linux interface indexes are not generally dense from zero, so the failure message can be noisy or misleading on systems where the enumerated position does not equal the kernel ifindex.

## Test Signals
Run `--netdev 1 --timeout 1 --verify` on Linux with normal and restricted privileges. Check that lack of optional ioctls is tolerated, at least loopback is discovered, and fatal errors are limited to unexpected ioctl failures. Build tests should cover systems without the required netdevice headers to confirm the unimplemented metadata path.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-netdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-netlink-proc.c -->
# sources/test-tools/stress-ng/stress-netlink-proc.c

## Purpose
`stress-netlink-proc.c` implements the `netlink-proc` stressor. It subscribes to Linux process connector events over `NETLINK_CONNECTOR`, creates short process chains, and counts recognized process events. This exercises connector delivery, process event parsing, fork/exit activity, and capability-gated netlink paths.

## Important APIs, Types, and Functions
The exported `stress_netlink_proc_info` registers the stressor with `CLASS_OS` and a `supported` callback. `stress_netlink_proc_supported()` requires `CAP_NET_ADMIN` through `stress_capabilities_check(SHIM_CAP_NET_ADMIN)`. `monitor()` receives and parses netlink messages, validating `nlmsghdr`, `cn_msg`, and `proc_event` payloads. `spawn_several()` recursively forks a bounded chain of children and changes process names to produce fork, exec-like name, wait, and exit activity. `stress_netlink_proc()` opens, binds, subscribes, runs, and closes the connector socket.

## Control Flow
The stressor creates a `PF_NETLINK`, `SOCK_DGRAM`, `NETLINK_CONNECTOR` socket and binds it to the process connector group using the current PID and `CN_IDX_PROC`. It builds a three-element `writev()` message containing an `nlmsghdr`, a `cn_msg` addressed to the process connector, and a `PROC_CN_MCAST_LISTEN` operation. After the global sync point, the run loop calls `spawn_several(args->name, 0, 5)` and then `monitor()`. `monitor()` receives one buffer, skips errors and no-op messages, validates connector IDs and payload sizes, and increments the bogo counter for recognized `PROC_EVENT_*` variants available for the compile-time kernel header version.

## State and Persistence
State is limited to the netlink socket and transient forked child processes. No process subscription state is explicitly unsubscribed before close; closing the socket releases it. Bogo counts are event driven and depend on kernel connector delivery. The process-name changes are transient per child.

## Dependencies and Integration Points
The stressor depends on Linux connector, netlink, and process connector headers, plus `writev`, `recv`, `fork`, and wait helpers. It integrates with stress-ng capability checks, logging, process naming, sync start, run-state transitions, and bogo counters. The event switch is guarded by `LINUX_VERSION_CODE` so the source can compile against older headers with fewer `PROC_EVENT_*` constants.

## Risks
This stressor will skip without `CAP_NET_ADMIN` or when the connector subsystem is unavailable. Netlink receive can drop events with `ENOBUFS`, which is treated as non-fatal, so bogo counts are not a complete process-event audit. `spawn_several()` recursively forks up to a small fixed depth, but repeated runs still create process churn and can interact with low `RLIMIT_NPROC`. The monitor reads one buffer per iteration, so high event rates can be coalesced or partially ignored.

## Test Signals
Validate unsupported behavior as an unprivileged user and event counting as a privileged user or with `CAP_NET_ADMIN`. Short runs should report bogo events and exit cleanly on timeout. Kernel/header compatibility tests should compile with and without connector headers and with older `LINUX_VERSION_CODE` definitions.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-netlink-proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-netlink-task.c -->
# sources/test-tools/stress-ng/stress-netlink-task.c

## Purpose
`stress-netlink-task.c` implements the `netlink-task` stressor. It uses generic netlink taskstats to repeatedly query task statistics for the running process, validating selected payload fields and exercising netlink request/response handling for task accounting.

## Important APIs, Types, and Functions
The stressor exports `stress_netlink_task_info` with `CLASS_OS`, `VERIFY_ALWAYS`, and a capability-based supported callback. `stress_nlmsg_t` is a compact message structure containing `nlmsghdr`, `genlmsghdr`, and 1 KiB payload storage. `stress_netlink_sendcmd()` builds and sends generic netlink commands with one attribute. `stress_parse_payload()` walks nested taskstats attributes and verifies the returned PID and monotonic non-decrease of `nivcsw`. `stress_netlink_taskstats_monitor()` sends repeated `TASKSTATS_CMD_GET` requests and parses replies. `stress_netlink_task()` opens the socket, discovers the taskstats family id, and enters the monitor loop.

## Control Flow
The stressor creates an `AF_NETLINK`, `SOCK_RAW`, `NETLINK_GENERIC` socket, binds it, then sends `CTRL_CMD_GETFAMILY` for `TASKSTATS_GENL_NAME`. It receives the family response, expects a `CTRL_ATTR_FAMILY_ID` attribute after the first attribute, and stores that id. After synchronization it repeatedly invokes `stress_netlink_taskstats_monitor()`. Each monitor iteration sends `TASKSTATS_CMD_GET` with `TASKSTATS_CMD_ATTR_PID` for the current process, receives a `stress_nlmsg_t`, checks `NLMSG_OK`, walks generic netlink attributes, and parses `TASKSTATS_TYPE_AGGR_PID` payloads. Every parsed response increments the bogo counter.

## State and Persistence
The stressor maintains only the socket, discovered family id, and the last seen involuntary context switch count. There are no durable writes. Any taskstats accounting consumed is kernel-provided runtime state. The `nivcsw` variable persists across monitor iterations to detect unexpected counter regressions.

## Dependencies and Integration Points
This is Linux-specific and requires connector, netlink, cn_proc, genetlink, and taskstats headers, plus `__linux__` generic netlink support. It depends on `CAP_NET_ADMIN`. It integrates with stress-ng state transitions, sync start, bogo counting, logging, and unimplemented-stressor metadata. It uses stress-ng shim memory helpers and branch annotations.

## Risks
The generic netlink family id parser assumes a particular attribute order in the family response by advancing to the second attribute and checking `CTRL_ATTR_FAMILY_ID`; more defensive parsing would walk all attributes. `stress_netlink_sendcmd()` returns success for `EAGAIN` and `EINTR`, so monitor logic may proceed to receive even if a request was not actually sent. Payload parsing uses kernel-structured data and careful length checks, but malformed or unexpected nested attributes can stop parsing early. The `numa_cpus` style bug is not present here, but capability and kernel config availability strongly affect runtime coverage.

## Test Signals
Run as unprivileged and privileged users to confirm skip and active paths. A short privileged run should count taskstats responses without PID mismatch or `nivcsw` regression messages. Tests should include kernels where taskstats generic netlink is absent, and builds without one or more required headers to verify the unimplemented path.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-netlink-task.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-ng.c -->
# sources/test-tools/stress-ng/stress-ng.c

## Purpose
`stress-ng.c` is the main program and orchestration layer for stress-ng. It parses global and stressor-specific options, builds the selected stressor list, prepares shared state, forks worker processes, manages synchronized starts and termination, aggregates counters and metrics, writes optional YAML output, and performs cleanup.

## Important APIs, Types, and Functions
The file defines process-wide globals such as `g_item_current`, `g_opt_timeout`, `g_opt_flags`, `g_pr_log_flags`, `g_stress_continue_flag`, `g_shared`, `g_error_env`, and `g_nowt`. It owns the static `stressors[]` table generated from the `STRESSORS` macro and the linked `stress_stressor_list_t` selection list. The PID-to-stats hash table maps child PIDs to `stress_stats_t` during reaping.

Key control functions include `stress_opts_parse()` for getopt dispatch, `stress_list_item_find()` and `stress_stressors_enable()` for list construction, `stress_shared_mmap()` for shared memory setup, `stress_stats_buffers_setup()` for assigning per-instance stats and metric buffers, `stress_run()` for forking all selected instances, `stress_child_run()` for the child lifecycle, `stress_stressors_wait()` and `stress_wait_status()` for reaping, `stress_metrics_set()` and `stress_metrics_dump()` for metric capture, and `main()` for end-to-end setup and teardown.

## Control Flow
`main()` fixes stressor names, initializes process naming and defaults, parses options, validates incompatible flags, applies ionice, scheduler, taskset, resctrl, timeout, random seed, NUMA mbind, job-file, logging, and class settings, then enables selected stressors. It excludes unsupported and pathological stressors, prepares signal handlers, chooses sequential, permutation, or parallel setup, allocates shared memory and locks, assigns stats buffers, starts auxiliary monitors, and finally calls the appropriate run mode.

`stress_run()` iterates selected stressors and instances, initializes sync state and stats, forks each child, and stores the child PID in the hash table. Children call `stress_child_run()`, which applies scheduler settings, installs handlers, sets OOM and timer behavior, initializes `stress_args_t`, invokes the selected `stressor_info_t->stressor`, records counters and checksums, gathers rusage, and exits with a stress-ng status code. The parent waits, maps statuses to pass/fail/skipped/metrics states, optionally aborts all workers on failure, and later dumps metrics and subsystem reports.

## State and Persistence
Most runtime state is in anonymous shared mappings rooted at `g_shared`, including per-instance `stress_stats_t`, shared helper pages, lock-backed shared heap, cache buffers, counters, checksum mappings, warning hashes, port maps, and optional perf, thermal, and RAPL data. The program also uses process-local linked lists, option settings, signal flags, and PID hash chains. Durable outputs are limited to configured logs, syslog, optional YAML, and stressor-created external artifacts elsewhere in the tree. Cleanup unmaps shared regions, destroys locks, frees stressor lists, closes logs, and exits with a status reflecting success, no resources, bad metrics, or core failure.

## Dependencies and Integration Points
This file integrates nearly every core module: options, settings, logging, locks, shared heap, memory, mmap, scheduler, affinity, cpuidle, ftrace, perf, klog, vmstat, smart, thermal zones, RAPL, resctrl, signals, OOM handling, job parsing, and stressor registration. Stressor implementations depend on the `stress_args_t` initialized here, shared bogo counter helpers from the header, `stress_metrics_set()`, and lifecycle states emitted through `stress_proc_state_set()`.

## Risks
The main risks are orchestration complexity and signal/fork interactions. Shutdown uses global flags, alarms, process kills, child wait state, and shared counters; regressions can leave workers running or misclassify exits. Metrics rely on child updates to shared memory plus checksum mirrors; forced kills can make counters untrustworthy. Option parsing binds an `-ops` option to `g_item_current`, so command ordering matters for associating operation limits. Several cleanup labels assume earlier initialization state is consistent. `stress_stats_hash_table_alloc()` sizes the hash table from the number of instances, so a zero-instance path must not reach PID hashing. The run modes adjust per-instance bogo limits differently, which is important for tests.

## Test Signals
High-value signals include compile coverage with optional subsystems enabled and disabled, `--help`, `--stressors`, `--verifiable`, invalid option combinations, dry-run, sequential, parallel, random, permutation, class selection, exclude and with lists, timeout behavior, abort-on-failure, YAML output, metrics output, and unsupported-stressor paths. Runtime tests should verify no child processes remain after SIGINT, SIGALRM timeout, and early stressor failure. Metrics tests should include a stressor that emits misc metrics and a forced-kill scenario that marks metrics untrustworthy.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-ng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-ng.h -->
# sources/test-tools/stress-ng/stress-ng.h

## Purpose
`stress-ng.h` is the central public header for the stress-ng source tree. It establishes feature-test macros, compiler detection, standard includes, common constants, stressor classes, process and statistics data structures, the shared memory ABI, global variables, bogo counter helpers, metric types, and exported core entry points used by individual stressors.

## Important APIs, Types, and Functions
The header defines exit codes (`EXIT_NO_RESOURCE`, `EXIT_NOT_IMPLEMENTED`, `EXIT_METRICS_UNTRUSTWORTHY`), stressor lifecycle states, class bits, memory units, operation limits, and bit helpers. Core data types include `stress_pid_t` for process tracking, `stress_counter_t` for bogo counters, `stress_args_t` for the per-stressor runtime contract, `stress_list_item_t` for selected stressors, `stress_metrics_info_t` and `stress_metrics_desc_t` for metrics, `stress_stats_t` for per-instance accounting, `stress_shared_t` for process-shared state, `stressor_info_t` for each stressor module's exported metadata, and `stress_stressor_t` for the registry.

Inline helpers such as `stress_continue_flag()`, `stress_continue_set_flag()`, `stress_bogo_stop()`, `stress_bogo_add()`, `stress_bogo_inc()`, `stress_bogo_set()`, `stress_force_killed_bogo()`, `stress_bogo_inc_lock()`, and `stress_instance_zero()` are used throughout stressor implementations. Exported functions include `stress_opts_parse()`, `stress_shared_readonly()`, `stress_shared_unmap()`, `stress_system_memory_info_log()`, `stress_metrics_set()`, `stress_stressor_find()`, `stress_bogo_max_ops_zero()`, and `stress_args_pid_find()`.

## Control Flow
The header does not run control flow directly, but it defines the contracts used by `stress-ng.c` and all stressors. The central loop contract is `stress_continue(args)`, which checks whether the local bogo counter is below `args->bogo.max_ops`; global termination is handled by `g_stress_continue_flag` and `stress_continue_set_flag()`, which also zeros all max-op counters. Bogo helpers toggle `counter_ready`, issue memory barriers, update counters, and mark readiness, enabling the main process to detect partially updated counters.

## State and Persistence
The important persistent runtime state is represented by `stress_shared_t`, an mmap-shared structure containing shared helper pages, heap, locks, instance counters, subsystem buffers, warning hashes, atomic scratch space, synchronization data, checksum mirrors, and a flexible array of `stress_stats_t`. This is not durable across runs, but it is the in-memory ABI between parent and child processes. The header also declares global process state stored in `stress-ng.c`.

## Dependencies and Integration Points
`stress-ng.h` includes `config.h`, standard C/POSIX headers, platform headers, and many core stress-ng headers: version, attributes, assembly, options, settings, signals, stack, logging, locks, memory, random, scheduler, stressor registry, sync, shims, time, helpers, and filesystem. Every stressor includes this header and exports a `stressor_info_t` referenced by the `STRESSORS(STRESSOR_INFO)` macro expansion. The header also provides compile-time portability shims for compilers, libc variants, feature-test macros, `MAP_ANONYMOUS`, `PATH_MAX`, branch prediction, and deprecated direct filesystem calls.

## Risks
Because this header is included broadly, changes to structure layout, macros, or inline helpers have tree-wide impact. `stress_shared_t`, `stress_args_t`, and `stress_stats_t` changes affect parent/child shared memory assumptions. Bogo counter helpers are intentionally lightweight but not fully atomic; they rely on memory barriers and a readiness flag rather than locks in the common path. The `stress_continue(args)` macro checks only the per-stressor counter limit, so stressors that do not also inspect `stress_continue_flag()` may not react immediately to global shutdown unless `stress_bogo_max_ops_zero()` has propagated. Feature-test macro changes can alter libc declarations and build behavior across platforms.

## Test Signals
Any edit here should trigger broad build coverage. Useful tests are full compilation with several compiler/libc combinations, stressor smoke runs that exercise bogo counters, metrics emission, signal shutdown, shared-memory allocation and unmapping, and optional subsystem toggles. ABI-sensitive changes should be checked with representative stressors that fork children, spawn threads, emit metrics, use shared helper pages, and run under timeout.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-ng.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-nice.c -->
# sources/test-tools/stress-ng/stress-nice.c

## Purpose
`stress-nice.c` implements the `nice` stressor. It repeatedly forks child processes that exercise `nice(2)`, `getpriority(2)`, and `setpriority(2)` across valid and invalid priority operations, stressing scheduler priority management and permission checks.

## Important APIs, Types, and Functions
The exported `stress_nice_info` registers a `CLASS_SCHEDULER | CLASS_OS` stressor with `VERIFY_ALWAYS`. `stress_nice_delay()` busy-yields for a short random duration to give priority changes scheduler-visible time. `stress_nice()` is the entry point. It uses `stress_capabilities_check(SHIM_CAP_SYS_NICE)`, `getrlimit(RLIMIT_NICE)`, `fork`, `shim_nice`, `getpriority`, `setpriority`, `stress_sched_settings_apply`, and `shim_waitpid`.

## Control Flow
The parent detects whether `CAP_SYS_NICE` is available and derives an assumed priority range, adjusted by `RLIMIT_NICE` where present. During the run loop it forks one child at a time. The child sets up failure injection, parent-death alarm, and scheduler settings. It probes whether raising priority is permitted, reads priorities for process/user/group selectors, and intentionally calls `setpriority()` with invalid selectors and IDs. It then either walks the configured setpriority range for its own PID or repeatedly calls `nice(1)` from -19 to 19. When `getpriority()` is available it checks that `nice(1)` does not increase the nice value by more than one step. The parent waits and propagates non-success exit status.

## State and Persistence
Priority changes are confined to the child process that exits at the end of each iteration. The parent keeps only the return code. No durable files or system settings are changed. Bogo counts are incremented by the child before exit; parent-side forced kill paths mark bogo state as force-killed when wait fails.

## Dependencies and Integration Points
The stressor depends on either `nice` or `setpriority`, and optionally `getpriority` and `RLIMIT_NICE`. It integrates with stress-ng capabilities, scheduler setup, kill helpers, parent-death alarm, process states, bogo counters, and stress-ng unimplemented metadata. It uses `core-killpid.h` to clean up children when wait fails.

## Risks
Priority semantics vary by platform, resource limit, user namespace, and capability set. The code assumes an approximate -20 to 20 priority range and adjusts it only when `RLIMIT_NICE` is available. Bogo increments happen in children, so abnormal child termination can make counters less reliable. The stressor intentionally invokes invalid `setpriority()` arguments, which should remain non-fatal but may produce platform-specific errno behavior.

## Test Signals
Run as a normal user and with `CAP_SYS_NICE` to cover both permission paths. Verify short timeout completion, no leaked child processes, and no false failure from valid `nice(1)` increments. Build tests should cover configurations with only `nice`, only `setpriority`, and neither to validate unimplemented fallback.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-nice.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-nop.c -->
# sources/test-tools/stress-ng/stress-nop.c

## Purpose
`stress-nop.c` implements the `nop` CPU stressor. It burns CPU cycles by executing architecture-specific no-op or low-impact instructions in tight loops, optionally selecting a random instruction variant. It also measures approximate nanoseconds per instruction.

## Important APIs, Types, and Functions
The file exports `stress_nop_info` with `CLASS_CPU` and an option `nop-instr`. `stress_nop_instr_t` maps instruction names to generated spin functions, optional CPU feature checks, and runtime ignore state. The `STRESS_NOP_SPIN_OP` macro generates loop bodies that execute an operation 64 x `NOP_LOOPS` times per inner iteration and update duration/count metrics. Architecture-specific operations include generic `stress_asm_nop`, x86 pause/tpause/serialize and multi-byte NOPs, ARM yield, PowerPC yield/mdoio/mdoom, and s390 nopr where available. `stress_nop_random()` samples non-random entries. `stress_sigill_nop_handler()` handles illegal instruction traps with `siglongjmp`. `stress_nop()` coordinates setup, execution, and metrics.

## Control Flow
At startup the stressor reads the selected `nop-instr` method and installs a `SIGILL` handler. If an instruction traps, the longjmp path marks the current instruction ignored, skips the stressor if even generic `nop` is illegal, or falls back to generic `nop` for fixed methods. After sync start, `stress_nop_callfunc()` performs the CPU feature check on first use, falls back to generic nop when unsupported, and then runs the selected spin loop until `stress_continue(args)` fails. Random mode repeatedly selects an instruction other than `random` and invokes it for one bounded spin block. At the end it stores a harmonic mean metric for nanoseconds per nop instruction.

## State and Persistence
The static `jmp_env` and `current_instr` support signal recovery. Each instruction entry caches whether its support check has run and whether it should be ignored. Duration and count are local to one stressor invocation and only the final metric is stored in stress-ng shared stats. There is no external persistent state.

## Dependencies and Integration Points
The stressor depends on architecture-specific assembly helper headers, `HAVE_ASM_NOP`, and `HAVE_SIGLONGJMP`. Optional CPU feature probes come from `core-cpu.h`. It integrates with stress-ng settings, signal handling, sync start, bogo counters, process states, random generator, and metric reporting. Unsupported builds still expose the `nop-instr` option through an unimplemented method callback.

## Risks
Instruction availability can differ between compiler target, CPU model, virtualization layer, and runtime feature bits; the SIGILL recovery path is critical. `current_instr` is static process state and must be valid when `SIGILL` fires. Random mode can repeatedly choose unsupported instructions until their ignore flags are cached. The timing metric measures loop wall time around large batches and is affected by frequency scaling, scheduler preemption, and instruction-specific wait behavior such as `tpause`.

## Test Signals
Run `--nop 1 --timeout 1 --metrics` and each exposed `--nop-instr` method on matching architectures. On x86, cover multi-byte nop variants and feature-gated `serialize` or `tpause` when available. Negative testing can force unsupported instruction selection on hardware lacking a feature and confirm graceful fallback instead of process death.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-nop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-null.c -->
# sources/test-tools/stress-ng/stress-null.c

## Purpose
`stress-null.c` implements the `null` stressor for `/dev/null`. It benchmarks or stresses writes to `/dev/null` and, unless `--null-write` is selected, also exercises miscellaneous operations such as `lseek`, `fcntl`, `ioctl`, `fallocate`, `fdatasync`, and Linux mmap-related paths.

## Important APIs, Types, and Functions
The exported `stress_null_info` registers a `CLASS_DEV | CLASS_MEMORY | CLASS_OS` stressor with `VERIFY_ALWAYS` and the `null-write` boolean option. `stress_null()` is the entry point. It uses `open("/dev/null", O_RDWR)`, `write`, `lseek`, `shim_fallocate`, `shim_fdatasync`, `fcntl(F_GETFL/F_SETFL)`, optional `ioctl(FIGETBSZ/FIONREAD)`, and Linux-only `mmap`, `msync`, and `munmap`.

## Control Flow
The stressor opens `/dev/null`, fills a 4096-byte aligned buffer, waits for synchronized start, and enters either write-only or mixed-operation mode. In write-only mode it writes the buffer until the run stops, tracking bytes and duration for throughput. In mixed mode it periodically times writes for metrics while also seeking to start/end/random offsets, issuing intentionally invalid fallocate/fdatasync-style operations for `/dev/null`, toggling selected file status flags, probing ioctls, and occasionally mapping an anonymous writable page using `/dev/null` as the fd argument while randomizing the offset. Each successful loop increments the bogo counter.

## State and Persistence
The only external object is the `/dev/null` file descriptor, closed before return. File status flags are restored after randomized `F_SETFL` changes when `F_GETFL` succeeds. Mapped pages are anonymous/private and unmapped immediately. The durable state is limited to metrics stored in stress-ng shared memory.

## Dependencies and Integration Points
The stressor depends on standard POSIX file APIs and optional Linux filesystem ioctl definitions. It uses stress-ng shims for memory, fallocate, fdatasync, msync, random values, logging, process states, sync start, bogo counters, and metrics. Unlike many stressors, there is no compile-time unimplemented fallback because `/dev/null` and the core APIs are assumed available enough for the baseline target.

## Risks
Some operations are intentionally invalid for `/dev/null`, so errno variance must remain non-fatal where ignored. The mixed mode measures only sampled write iterations to avoid timing every operation, so reported throughput is approximate. The Linux mmap call uses `MAP_PRIVATE | MAP_ANONYMOUS` with a file descriptor and randomized offset; this is unusual but should ignore the fd due to `MAP_ANONYMOUS` on Linux. Systems without `/dev/null` or with nonstandard semantics fail early.

## Test Signals
Run both `--null 1 --timeout 1 --metrics` and `--null 1 --null-write --timeout 1 --metrics`. Verify clean handling of ignored invalid operations, metric emission for MB/s write rate, and no descriptor leaks. Platform tests should cover builds with and without optional ioctl constants.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-null.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-numa.c -->
# sources/test-tools/stress-ng/stress-numa.c

## Purpose
`stress-numa.c` implements the `numa` stressor. It exercises Linux NUMA memory policy syscalls by allocating a shared memory region, binding and moving pages among NUMA nodes, probing invalid syscall arguments, checking page data integrity, and recording NUMA hit/miss style metrics.

## Important APIs, Types, and Functions
The stressor exports `stress_numa_info` with `CLASS_CPU | CLASS_MEMORY | CLASS_OS`, `VERIFY_ALWAYS`, and options `numa-bytes`, `numa-shuffle-addr`, and `numa-shuffle-node`. `stress_numa_stats_t` stores aggregate `numa_hit` and `numa_miss` readings. `stress_numa_stats_read()` scans `/sys/devices/system/node/node*/numastat`. `stress_numa_check_maps()` inspects `/proc/self/numa_maps` for the node backing a mapping. `stress_numa()` allocates masks and memory, runs `get_mempolicy`, `set_mempolicy`, `mbind`, `migrate_pages`, `move_pages`, and metric collection.

## Control Flow
The stressor derives memory size from settings and instance count, allocates NUMA masks for available nodes, and maps arrays for page statuses, destination nodes, page pointers, and the data buffer. It reads baseline NUMA stats, synchronizes, chooses an initial node, and enters a loop. Each iteration probes current policy and invalid `get_mempolicy` cases, sets random or invalid policies, touches memory, gets CPU/node information, binds the buffer to a node with `mbind`, sets home nodes, exercises invalid `mbind` cases, optionally checks privilege behavior for `MPOL_MF_MOVE_ALL`, migrates process pages, and then repeatedly builds page and destination arrays for `move_pages`.

Within the `move_pages` section it can shuffle page addresses and destination nodes, writes each page's own address into the page for integrity checking, moves pages, checks `/proc/self/numa_maps` for the first buffer page, verifies page contents, and touches pages again. It also probes invalid `move_pages` calls such as bad PID, zero pages, invalid flags, invalid address, invalid destination node, and null nodes. After the loop it computes metrics from sysfs counters and mapping checks.

## State and Persistence
All mappings are anonymous and released before return. NUMA memory policy changes are process-local and end with process exit, though they can influence the stressor while it runs. Metrics are persisted to shared stats. The code reads sysfs and procfs but does not write durable files.

## Dependencies and Integration Points
This Linux-only stressor requires syscall numbers for `get_mempolicy`, `mbind`, `migrate_pages`, `move_pages`, and `set_mempolicy`, plus Linux mempolicy constants. It integrates with `core-numa` mask helpers, mmap population helpers, madvise helpers, stress-ng settings, capabilities, process states, memory usage reporting, bogo counters, and metrics.

## Risks
NUMA syscall behavior depends heavily on kernel config, cpuset/cgroup policy, permissions, and hardware topology. The stressor tolerates `ENOSYS`, `EIO`, and some permission failures, but unexpected errno values become failures. Memory size is rounded by page size and per-instance count, so many instances can still create significant memory pressure. Parsing `/proc/self/numa_maps` is format-sensitive. Data verification stops after repeated mismatches, which can indicate page movement corruption or writes through unexpected aliases.

## Test Signals
Run on a NUMA-capable Linux system with short timeouts and both shuffle options. Also run on a single-node or NUMA-disabled system to confirm skip behavior. Privileged and unprivileged runs should cover `MPOL_MF_MOVE_ALL` permission checks. Metrics should include NUMA hits/misses when sysfs is readable and checked-page percentage when `/proc/self/numa_maps` exposes matching entries.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-numa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-numacopy.c -->
# sources/test-tools/stress-ng/stress-numacopy.c

## Purpose
`stress-numacopy.c` implements the `numacopy` stressor. It allocates one page per NUMA node, binds each page to a target node, repeatedly copies data between every node pair, optionally changes CPU affinity, and reports page fill/copy rates and a per-node copy-rate table.

## Important APIs, Types, and Functions
The exported `stress_numacopy_info` is a `CLASS_CPU | CLASS_MEMORY | CLASS_OS` stressor with `VERIFY_ALWAYS` and options `numacopy-affinity` and `numacopy-mode`. `stress_numacopy_metric_t` tracks duration and rate per node pair. `stress_numacopy_cpus_t` stores CPUs associated with a NUMA node. `stress_numacopy_mode_t` and `stress_numacopy_affinity_t` define option tables. `stress_numacopy_exercise()` performs the copy workload and optional affinity switching. `stress_numacopy_affinity_supported()` checks scheduler affinity support. `stress_numanode_cpus()` parses sysfs `cpulist` files. `stress_numacopy()` allocates memory, binds pages, runs the workload, reports metrics, and cleans up.

## Control Flow
The stressor reads mode and affinity options, validates affinity support, discovers NUMA nodes, limits to 64 nodes, optionally builds a per-node CPU list, allocates a metrics matrix sized `nodes * nodes`, maps a pointer array and a local page, then maps one private page per NUMA node. Each node page is bound with `shim_mbind()` using the selected memory policy mode and `MPOL_MF_MOVE | MPOL_MF_STRICT`.

After synchronized start, the run loop calls `stress_numacopy_exercise()`. That function periodically changes CPU affinity according to the selected policy: current node, next node, previous node, random CPU, or none. For every source node and destination node pair it fills the local page, copies to source then destination, verifies the first byte, then fills and copies in the reverse direction. It accumulates per-pair duration and global copy/fill operation counts and increments the bogo counter. Instance zero prints a copy-rate matrix and the stressor publishes aggregate pages-filled and pages-copied metrics.

## State and Persistence
The stressor creates anonymous mappings for the page pointer array, local page, and per-node pages, all unmapped during cleanup. CPU affinity changes affect the stressor process while it runs; the code does not restore the original affinity before exit. Metrics live in process memory until reported into shared stats. It reads NUMA CPU topology from sysfs and does not write durable state.

## Dependencies and Integration Points
This Linux-oriented stressor requires `mbind` syscall support and NUMA mask helpers. It optionally depends on `sched_getaffinity` and `sched_setaffinity`, sysfs node CPU lists, and mempolicy constants such as `MPOL_BIND`, `MPOL_INTERLEAVE`, `MPOL_PREFERRED`, and `MPOL_WEIGHTED_INTERLEAVE`. It integrates with stress-ng target clones, mmap population, memory naming, memory usage reporting, bogo counters, metrics, logging, settings, and process states.

## Risks
There are several implementation-sensitive areas. `numa_cpus` is allocated with `max_cpus` entries but indexed by NUMA node up to `num_numa_nodes`; systems with more nodes than configured CPUs could index beyond the allocation. In the page-binding loop, the NUMA mask is not cleared between nodes before `STRESS_SETBIT`, so later `mbind` calls may include all previous nodes rather than only the current node. `stress_numacopy_affinity_supported()` has a non-void function path under missing affinity APIs that logs but does not explicitly return a value. The cpulist parser stops when it reaches a non-digit separator and may not advance past commas, so multi-range lists can be underparsed. The stressor can print a large matrix and consume noticeable CPU and memory bandwidth on many-node systems.

## Test Signals
Run with `--numacopy 1 --timeout 1 --metrics` on single-node and multi-node systems. Cover each `--numacopy-mode` exposed at build time and each affinity mode, especially `node`, `next`, `prev`, and `random`. Use systems or mocks with comma-separated cpulists to validate parsing. Sanitizer or bounds-checking runs are valuable for the `numa_cpus` node-vs-CPU allocation risk.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-numacopy.c -->
