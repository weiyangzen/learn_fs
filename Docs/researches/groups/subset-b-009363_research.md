# subset-b-009363 research

This grouped report covers the requested `sources/test-tools/stress-ng` core helpers, packaging tests, kernel coverage harness, and early alphabetic stressors. Each section is wrapped with the required source-path markers for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-stack.h -->
# sources/test-tools/stress-ng/core-stack.h

## Purpose
`core-stack.h` declares stack utility APIs used by stressors and signal-handling paths to reason about stack direction, alternate signal stacks, stack-top alignment, stack-smash checking, and backtraces.

## Important APIs, Types, And Functions
`STRESS_SIGSTKSZ` and `STRESS_MINSIGSTKSZ` resolve through runtime helpers rather than compile-time constants. `stress_align_stack` masks a stack-top pointer down to a 16-byte boundary. The exported API includes `stress_stack_direction`, `stress_stack_top`, `stress_stack_sigalt_no_check`, `stress_stack_sigalt`, `stress_stack_sigalt_disable`, `stress_stack_sigstksz`, `stress_stack_minsigstksz`, `stress_stack_smash_check_flag_set`, and `stress_stack_backtrace`.

## Control Flow
Callers allocate or locate a stack region, compute the architecture-correct top with `stress_stack_top`, optionally align it, and install or disable an alternate signal stack. Stack-size macros defer to implementation code so platform-specific signal-stack sizes can be handled centrally.

## State And Persistence
The header itself stores no state. The implementation behind these declarations likely owns process-local signal-stack state and a stack-smash check flag. No persistent filesystem state is involved.

## Dependencies And Integration Points
It includes `stress-ng.h` for common attributes, types, and platform feature definitions. Integration points are signal stressors, alternate-stack tests, backtrace/debug paths, and any stressor that allocates stacks manually.

## Risks
Stack alignment and direction handling are architecture-sensitive; wrong assumptions can corrupt call frames or signal delivery. Alternate signal stack sizes vary across libc/kernel combinations, so compile-time constants are intentionally avoided. Backtrace behavior may be unavailable or unsafe in signal contexts depending on platform.

## Test Signals
Build coverage validates declarations across platforms. Runtime signals come from stack-oriented stressors, signal stressors using alternate stacks, and command-line cases such as `--stack`, `--stackmmap`, and backtrace-on-failure paths.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-stack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-stressors.h -->
# sources/test-tools/stress-ng/core-stressors.h

## Purpose
`core-stressors.h` is the central X-macro registry of stress-ng stressors. It defines the canonical stressor list and macro adapters for enum entries, runtime table elements, and external `stress_*_info` declarations.

## Important APIs, Types, And Functions
`STRESSORS(MACRO)` expands hundreds of stressor identifiers, including this subset's `access`, `acl`, `acct`, `af_alg`, and `affinity`. `STRESSOR_ENUM(name)` emits `STRESS_name` enum values, `STRESSOR_ELEM(name)` emits runtime stressor table rows containing `&stress_name_info`, option IDs, operation IDs, and string names, and `STRESSOR_INFO(name)` emits extern declarations for each `stressor_info_t`.

## Control Flow
The file has no runtime logic. It is included by `stress-ng.c` or related registry code with different macro definitions so the same ordered list generates multiple synchronized structures. Adding, removing, or renaming a stressor changes command-line availability, option dispatch, and info-object linkage.

## State And Persistence
No runtime state is stored here. Its persistent effect is compile-time: the list determines which stressors are represented in the binary and in generated option/help tables.

## Dependencies And Integration Points
It depends on naming conventions across stressor source files: each `MACRO(foo_bar)` must match `stress_foo_bar_info`, `OPT_foo_bar`, and `OPT_foo_bar_ops`. Debian autopkgtests and `kernel-coverage.sh` discover stressors through `stress-ng --stressors`, which is built from this registry.

## Risks
The registry is a high-blast-radius compile-time contract. A missing info object, option constant, or inconsistent underscore spelling causes build failures; incorrect ordering can affect enum/table assumptions. Because shell tests iterate `--stressors`, newly listed stressors are automatically exercised and may need skip rules.

## Test Signals
Successful full build is the primary test. `debian/tests/fast-test-all` enumerates the registry through `--stressors`, while `debian/tests/lite-test` and `kernel-coverage.sh` explicitly exercise many registered names and expose broken table wiring quickly.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-stressors.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-sync.c -->
# sources/test-tools/stress-ng/core-sync.c

## Purpose
`core-sync.c` implements shared PID/state management for coordinated stressor startup, especially `--sync-start`, and provides a PID lookup tree used by parent/reaper logic.

## Important APIs, Types, And Functions
`stress_sync_s_pids_mmap` and `stress_sync_s_pids_munmap` allocate shared `stress_pid_t` arrays. `stress_sync_start_init`, `stress_sync_start_wait_s_pid`, `stress_sync_start_wait`, `stress_sync_start_cont_s_pid`, and `stress_sync_start_cont_list` coordinate child stop/continue behavior using `SIGSTOP`/`SIGCONT`. `stress_sync_init_pids`, `stress_sync_order_pid`, and `struct_sync_find_pid` initialize and organize PID records in a hash-balanced binary tree. The internal `stress_sync_order_pid_hash` reverses PID bits via `core-bitops` helpers.

## Control Flow
Parents mmap shared PID records and initialize them to waiting state. Children set their PID, mark themselves waiting, stop themselves when `OPT_FLAGS_SYNC_START` is active, then mark running once continued. The parent polls the linked list until all live children are waiting or finished, sends `SIGCONT` to each, and waits until states report running or finished. PID tree insertion uses reversed PID bits to avoid a degenerate tree for monotonically increasing PIDs.

## State And Persistence
State is shared anonymous memory containing `stress_pid_t` fields such as PID, child PID, state, tree links, reaped flag, and wait status. It is process-shared but not persistent after munmap/process exit. `stress_sync_start_timeout` arms per-process `alarm()` based on `g_opt_timeout`.

## Dependencies And Integration Points
This module depends on `stress-ng.h`, `core-bitops.h`, `core-sync.h`, `mmap`, signals, shared global flags, and timing helpers. Stressors that fork helper children, including `stress-access.c` and `stress-affinity.c`, use this module to synchronize worker starts and maintain reaper state.

## Risks
The fallback non-atomic state store/load path is intentionally racy and relies on polling tolerance. Stopped children must always be continued or killed during cleanup; otherwise test runs can leave suspended processes. PID-hash collisions are possible because lookup compares only the reversed hash, so correctness depends on the transform being one-to-one for the platform PID width.

## Test Signals
Runtime coverage comes from any stressor using `--sync-start`, plus multi-process stressors such as access and affinity. Failures show up as hung starts, missed SIGCONT, unreaped children, or incorrect PID lookup during cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-sync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-sync.h -->
# sources/test-tools/stress-ng/core-sync.h

## Purpose
`core-sync.h` exposes the process-start synchronization API and inline state accessors used by stressors that coordinate forked workers.

## Important APIs, Types, And Functions
The header defines the state constants `STRESS_SYNC_START_FLAG_WAITING`, `STARTED`, `RUNNING`, and `FINISHED`. It declares shared PID array allocation, start wait/continue helpers, PID initialization, PID tree insertion, and PID lookup. Inline helpers `stress_sync_state_store` and `stress_sync_state_load` use sequentially consistent compiler atomics when available, and `stress_sync_start_s_pid_list_add` pushes a record onto a linked list.

## Control Flow
Callers initialize `stress_pid_t` records, add active records to a list, let children wait through `stress_sync_start_wait*`, and let parents continue the list when all children reach the waiting state. State transitions flow waiting to running to finished, with started used during initialization.

## State And Persistence
The only state touched by the header is the caller-owned `stress_pid_t` memory, commonly shared anonymous mmap memory. No filesystem persistence exists.

## Dependencies And Integration Points
It depends on `stress_pid_t`, `stress_args_t`, attribute macros, atomic builtins, and global sync-start flags from `stress-ng.h`. It is included by `core-sync.c` and stressors that fork children directly.

## Risks
Consumers must keep the linked list and tree links distinct and must not reuse a `stress_pid_t` without reinitialization. The non-atomic fallback can require polling loops and may be weak on unusual memory models. State constants are part of the parent/child protocol, so changes must be coordinated with `core-sync.c`.

## Test Signals
Build coverage validates atomic feature guards. Runtime signals come from `--sync-start` in multi-process stressors; stuck waiting, premature start, or missing child continuation indicates header/API misuse.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-sync.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-syslog.h -->
# sources/test-tools/stress-ng/core-syslog.h

## Purpose
`core-syslog.h` provides portability wrappers around syslog APIs so logging call sites can compile even when `<syslog.h>` is unavailable.

## Important APIs, Types, And Functions
When `HAVE_SYSLOG_H` is defined, `shim_syslog`, `shim_openlog`, and `shim_closelog` map directly to `syslog`, `openlog`, and `closelog`. Otherwise they expand to no-op macros.

## Control Flow
There is no runtime control flow in the header. Preprocessor feature detection selects real syslog calls or no-op behavior at compile time.

## State And Persistence
With syslog support, process logging can persist to the host logging system according to syslog configuration. Without support, no state is stored and calls disappear at compile time.

## Dependencies And Integration Points
It depends on `HAVE_SYSLOG_H` from configure/build detection and on callers including system syslog definitions when available through the common headers. It integrates with stress-ng's `--syslog` behavior and long-running coverage scripts that enable syslog logging.

## Risks
The variadic `shim_syslog` macro requires at least one variadic argument in supported builds. In unsupported builds, logging side effects inside arguments vanish because the macro expands to nothing. Callers must not rely on syslog calls for required control flow.

## Test Signals
Compile tests on systems with and without syslog are the main signal. Runtime coverage comes from `kernel-coverage.sh` and stress-ng invocations with `--syslog`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-syslog.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-target-clones.h -->
# sources/test-tools/stress-ng/core-target-clones.h

## Purpose
`core-target-clones.h` centralizes compiler `target_clones` attribute selection for CPU-dispatched optimized functions.

## Important APIs, Types, And Functions
The public output is the `TARGET_CLONES` macro. On supported x86 builds it can expand to `__attribute__((target_clones(...)))` with MMX, SSE, AVX, Intel microarchitecture, and AMD `znver` targets plus `default`. On supported PPC64 builds it can include Power9, Power10, and Power11 targets. ICC and small builds disable target clones.

## Control Flow
There is no runtime logic in this header, but compiled functions annotated with `TARGET_CLONES` gain compiler-generated runtime dispatch. The preprocessor builds `TARGET_CLONES_ALL` only when architecture, compiler, and individual target probes are present; otherwise `TARGET_CLONES` becomes empty.

## State And Persistence
No source-level mutable state exists. The compiled binary may contain multiple function versions and dispatch thunks, which affects code size and runtime CPU feature selection.

## Dependencies And Integration Points
It includes `core-arch.h` and uses many build-time feature macros. `core-workload.c` uses `TARGET_CLONES` on math, memory-read, and vector workload helpers; other performance-sensitive stressors may include it.

## Risks
Target strings are compiler-version sensitive. Enabling an unsupported target can fail compilation or produce illegal instructions if compiler dispatch is incorrect. Disabling target clones for small builds and ICC prevents known compatibility and binary-size issues.

## Test Signals
Builds across x86, PPC64, GCC, Clang, musl, ICC, and `HAVE_BUILD_SMALL` configurations validate this header. Runtime workload and vector stressors exercise the generated dispatch paths.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-target-clones.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-thermal-zone.c -->
# sources/test-tools/stress-ng/core-thermal-zone.c

## Purpose
`core-thermal-zone.c` discovers Linux thermal zones, samples their temperatures, and emits per-stressor thermal summaries in human-readable and YAML output.

## Important APIs, Types, And Functions
`stress_tz_init` scans `/sys/class/thermal/thermal_zone*/type`, normalizes type names, de-duplicates repeated type names with an instance counter, sorts insertion by type, and assigns stable indices. `stress_tz_free` releases the linked list. `stress_tz_temperatures_get` reads `temp` files into a `stress_tz_t` sample. `stress_tz_dump` aggregates recorded temperatures across stressor instances and writes informational/YAML output. Internal helpers include `stress_tz_type_instance`, `stress_tz_type_fix`, `stress_tz_insert`, and `stress_tz_compare`.

## Control Flow
Initialization walks thermal-zone directory entries up to `STRESS_THERMAL_ZONES_MAX`, allocates a node per valid zone, reads and sanitizes the type, inserts the node in lexical order, and then assigns indices. During stressor runs, samples are stored by zone index. At report time, the code copies zone pointers into an array, sorts by type and instance, averages valid temperatures at or below 250 C across non-ignored stressor instances, and prints per-stressor readings.

## State And Persistence
The persistent system data is read-only sysfs state. Runtime state is the linked list in `g_shared->tz_info` and per-stressor `tz_stat` arrays. The module allocates heap memory for paths/types and temporary arrays, all freed by `stress_tz_free` or local cleanup.

## Dependencies And Integration Points
It depends on Linux thermal sysfs layout, `core-sort.h` for `shim_qsort`, `stress_list_item_t` statistics, shared globals, and YAML/log output helpers. `core-vmstat.c` uses the discovered list for periodic `--thermalstat` output.

## Risks
Sysfs may be absent, incomplete, dynamically changing, or expose unexpected names. Any failure to read a type aborts initialization with `-1`, which may disable thermal reporting more broadly than necessary. The fixed maximum of 31 zones bounds memory but can omit zones on large systems.

## Test Signals
Runtime signals come from `--tz`, `--thermalstat`, and kernel coverage runs that enable thermal output. Machines without thermal zones should report unavailable temperatures rather than failing stressor execution.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-thermal-zone.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-thermal-zone.h -->
# sources/test-tools/stress-ng/core-thermal-zone.h

## Purpose
`core-thermal-zone.h` defines the thermal-zone data structures and API used for sampling and reporting per-stressor temperature data.

## Important APIs, Types, And Functions
It defines `STRESS_THERMAL_ZONES`, `STRESS_THERMAL_ZONES_MAX`, `stress_tz_info_t`, `stress_tz_stat_t`, and `stress_tz_t`. Exports include `stress_tz_init`, `stress_tz_free`, `stress_tz_temperatures_get`, and `stress_tz_dump`.

## Control Flow
Callers initialize a linked list of zones, collect temperatures into fixed-size per-stressor arrays during execution, dump aggregated results at reporting time, then free the list.

## State And Persistence
The structures hold heap-owned path/type strings, zone ordering metadata, and millidegree-Celsius samples. This is process/shared-memory reporting state only; sysfs is read but not modified.

## Dependencies And Integration Points
It depends on `FILE`, `stress_list_item_t`, and common stress-ng types from the broader include stack. It integrates with `core-vmstat.c`, shared runtime state, YAML reports, and thermal-stat command-line options.

## Risks
The fixed-size `tz_stat` array requires every index to remain below `STRESS_THERMAL_ZONES_MAX`. Consumers must free strings and list nodes exactly once. The unconditional `STRESS_THERMAL_ZONES` definition means non-Linux builds must rely on implementation guards rather than header-level exclusion.

## Test Signals
Compilation validates structure availability. Runtime coverage comes from `--tz`, `--thermalstat`, YAML metric dumps, and machines with multiple duplicated thermal-zone type names.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-thermal-zone.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-thrash.c -->
# sources/test-tools/stress-ng/core-thrash.c

## Purpose
`core-thrash.c` implements the optional background memory-thrashing helper used to perturb system memory, page cache, NUMA placement, KSM, slab reclaim, and process page residency while other stressors run.

## Important APIs, Types, And Functions
The public API is `stress_thrash_start` and `stress_thrash_stop` with no-op stubs when unavailable. Internals include signal handlers `stress_thrash_handler` and `stress_thrash_pagein_handler`, `/proc/<pid>/maps` parsing via `stress_thrash_read_proc_maps`, page-in routines `stress_thrash_pagein_self`, `stress_pagein_proc`, and `stress_thrash_pagein_all_procs`, sysfs/proc writers such as `stress_thrash_compact_memory`, `stress_thrash_zone_reclaim`, `stress_thrash_kmemleak_scan`, `stress_thrash_slab_shrink`, `stress_thrash_drop_caches`, and `stress_thrash_merge_memory`, plus NUMA/mapping perturbation helpers such as `stress_thrash_move_pages` and `stress_thrash_fragment_mappings`.

## Control Flow
On supported Linux builds, `stress_thrash_start` forks a helper, records parent/child PIDs, installs signal handlers, may raise scheduling priority, and loops while `thrash_run` and the parent are alive. The loop reads kernel memory knobs, walks process maps, pages in readable mappings, tries NUMA page migration where available, fragments mappings, and triggers reclaim/compaction/KSM-style operations. `stress_thrash_stop` signals and waits for the helper.

## State And Persistence
Runtime state includes `thrash_pid`, `parent_pid`, `thrash_run`, and signal jump buffers. The helper reads `/proc` and `/sys`, and may write to kernel control files such as compaction, drop-caches, KSM, slab shrink, kmemleak, and zone reclaim controls depending on permissions. It does not persist project files, but it deliberately changes kernel VM behavior during a run.

## Dependencies And Integration Points
It depends on Linux `/proc`, `/sys`, signal handling, `core-mmap`, `core-numa`, `core-killpid`, scheduler APIs, and stress-ng global continue flags. It is enabled by stressors/options that request memory thrashing, for example coverage-script cases using `--thrash`.

## Risks
This is intentionally intrusive. Kernel knobs may require privileges, may be absent, or may have system-wide effects. Parsing `/proc/<pid>/maps` is format-sensitive. Signal/longjmp cleanup must avoid leaving helpers running. NUMA and move-pages paths are highly platform- and privilege-dependent.

## Test Signals
Runtime coverage comes from memory stressors invoked with `--thrash` in `kernel-coverage.sh`, plus manual runs on Linux with and without NUMA and privileged sysfs access. Expected non-support should degrade to skipped or no-op behavior rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-thrash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-thrash.h -->
# sources/test-tools/stress-ng/core-thrash.h

## Purpose
`core-thrash.h` exposes the background memory-thrashing lifecycle API.

## Important APIs, Types, And Functions
It declares `stress_thrash_start` and `stress_thrash_stop`. The start function returns a status code, while stop performs helper teardown.

## Control Flow
Callers start the thrash helper before or during a stressor run and call stop during cleanup. Unsupported builds still provide the same API through stub implementations in `core-thrash.c`.

## State And Persistence
No state is defined in the header. Implementation state is process-local helper PID and signal state, with possible system VM side effects while active.

## Dependencies And Integration Points
The header is included by stressors or core orchestration code that honors `--thrash`. It relies on common stress-ng declarations included before or through implementation files.

## Risks
Callers must pair start/stop to avoid orphan helpers. Because the implementation may touch system-wide memory controls, lifecycle mistakes have broader impact than ordinary per-process stressors.

## Test Signals
Build coverage validates universal API availability. Runtime signals come from stressors using `--thrash`, especially the kernel coverage script's memory and `brk`/`mmap` cases.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-thrash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-time.c -->
# sources/test-tools/stress-ng/core-time.c

## Purpose
`core-time.c` provides common wall-clock timestamp helpers and human-readable duration formatting.

## Important APIs, Types, And Functions
`stress_time_timeval_to_double` converts `timeval` to seconds. `stress_time_now` returns seconds as a `double`, preferring `clock_gettime(CLOCK_REALTIME)` through `stress_time_now_timespec` and falling back to `gettimeofday` through `stress_time_now_timeval` after a failure. `stress_time_duration_to_str` formats seconds into years, days, hours, minutes, and seconds using the internal `stress_format_time`.

## Control Flow
The first call path uses the current function pointer, initially the timespec implementation. If it fails, `stress_time_now` swaps the pointer to the timeval implementation and retries. Duration formatting emits only nonzero larger units, optionally forces seconds, and returns `"0 secs"` when nothing was emitted.

## State And Persistence
The only mutable state is the static function pointer `stress_time_now_func` and the static output buffer in `stress_time_duration_to_str`. No persistent data is written.

## Dependencies And Integration Points
It depends on libc time APIs, stress-ng numeric constants, attribute macros, and safe string helpers. Timing is consumed broadly by stressor loops, metrics, status output, throttling, and reports.

## Risks
`stress_time_duration_to_str` returns a static buffer and is not thread-safe across simultaneous callers. `CLOCK_REALTIME` can move with wall-clock adjustments; duration-sensitive code may prefer monotonic time but this helper intentionally reports wall time. The function-pointer fallback is global and unsynchronized.

## Test Signals
Runtime signals include stressor loop timing, metrics rates, `--status` elapsed-time output, and tests that run on systems without `clock_gettime`. Formatting issues are visible in status and YAML/log reports.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-time.h -->
# sources/test-tools/stress-ng/core-time.h

## Purpose
`core-time.h` declares the common time conversion, current-time, and duration-formatting helpers.

## Important APIs, Types, And Functions
Exports are `stress_time_timeval_to_double`, `stress_time_now`, and `stress_time_duration_to_str`. Attributes mark conversion as `CONST` and duration formatting as non-null returning.

## Control Flow
Callers use `stress_time_now` for loop deadlines and metric deltas, and `stress_time_duration_to_str` for display strings. The header does not define runtime logic.

## State And Persistence
No state is defined here. Implementation state includes a static fallback function pointer and static formatting buffer.

## Dependencies And Integration Points
It includes `core-attribute.h` and relies on `struct timeval`, `bool`, and common type visibility from the include environment. Nearly every stressor can indirectly depend on this API for timing and metrics.

## Risks
The static-buffer return contract is not visible in the prototype, so callers must not store the returned pointer across later formatting calls. Include ordering must provide system time and boolean types.

## Test Signals
Build coverage across platforms and runtime metric/status output validate the API. Any change that alters return precision or buffer lifetime can affect many stressors.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-try-open.c -->
# sources/test-tools/stress-ng/core-try-open.c

## Purpose
`core-try-open.c` safely probes whether a potentially blocking file or device can be opened without hanging the main stressor.

## Important APIs, Types, And Functions
`stress_try_open` forks a child to perform `open(path, flags)`, polls it with `waitpid(..., WNOHANG)`, and kills it if the timeout is exceeded. `stress_try_open_timeout` either uses POSIX timers and `SIGRTMIN` to interrupt a direct `open`, or falls back to plain `open` when timer support is unavailable. The internal `stress_try_kill` repeatedly signals and waits for a stuck child, then logs process info.

## Control Flow
`stress_try_open` first stats the path, forks, lets the child arm a short alarm and attempt open, then maps child exit status to `STRESS_TRY_OPEN_*` codes. The parent polls for a bounded number of retries based on the requested timeout, forcibly kills on wait errors or timeout, and handles vanished children. The timer-based variant installs a signal handler, creates a realtime timer for the timeout, calls open, deletes the timer, and restores errno.

## State And Persistence
No persistent project state is written. The code creates temporary child processes and a process-local POSIX timer. It may leave system-level traces only through logs and process info when a child cannot be killed.

## Dependencies And Integration Points
It depends on fork/wait/kill, `core-killpid`, `core-signal`, `stress_process_info`, stat/open shims, and stress-ng continue flags. Device and filesystem stressors can use it before touching risky paths.

## Risks
The helper deliberately handles broken drivers that may block in open forever, but an unkillable D-state child can still remain until the kernel releases it. `stress_try_open_timeout` uses `SIGRTMIN`, so signal-handler conflicts must be avoided. Returning `-1` for pre-stat failure differs from the defined positive status codes.

## Test Signals
Coverage comes from stressors that probe devices or special files and from error paths on busy/missing devices. Hangs, unreaped children, or lost errno after timeout are key failure signals.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-try-open.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-try-open.h -->
# sources/test-tools/stress-ng/core-try-open.h

## Purpose
`core-try-open.h` defines status codes and prototypes for bounded-risk open probes.

## Important APIs, Types, And Functions
Status codes are `STRESS_TRY_OPEN_OK`, `STRESS_TRY_OPEN_FORK_FAIL`, `STRESS_TRY_OPEN_WAIT_FAIL`, `STRESS_TRY_OPEN_EXIT_FAIL`, `STRESS_TRY_OPEN_FAIL`, and `STRESS_TRY_AGAIN`. The exported functions are `stress_try_open` and `stress_try_open_timeout`.

## Control Flow
Callers invoke one of the probe helpers with a path, flags, and nanosecond timeout. Results distinguish success, retryable device-busy/resource cases, child-management failures, and open failure.

## State And Persistence
No state is declared in the header. Implementation state is transient child/timer state.

## Dependencies And Integration Points
It depends on `stress_args_t` and common integer/time types from `stress-ng.h`. Stressors that handle special files, drivers, or devices integrate with these return codes to skip or retry safely.

## Risks
Callers must handle both the documented status constants and `-1` from the implementation's pre-stat failure. Misinterpreting `STRESS_TRY_AGAIN` as hard failure can reduce coverage on temporarily busy devices.

## Test Signals
Build coverage validates prototypes. Runtime signals appear in device/file stressors that skip problematic paths instead of hanging.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-try-open.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-vecmath.h -->
# sources/test-tools/stress-ng/core-vecmath.h

## Purpose
`core-vecmath.h` gates vector-math support for compilers and architectures with known vector-code issues.

## Important APIs, Types, And Functions
The header may undefine `HAVE_VECMATH` when Clang is older than 5 or when GCC older than 6 is used on PPC/PPC64. It exports no functions or types.

## Control Flow
Compile-time feature checks either preserve vector math support or force scalar fallback code in including files such as `core-workload.c`.

## State And Persistence
No runtime state or persistent state exists.

## Dependencies And Integration Points
It includes `core-arch.h` for architecture macros and depends on compiler feature definitions. Vector-capable stressors use `HAVE_VECMATH` to select explicit vector types and operations.

## Risks
The guards encode historical compiler behavior. Removing them can reintroduce very slow or broken builds; over-broad guards can hide useful vector coverage on fixed toolchains.

## Test Signals
Cross-compiler builds are the main signal. Runtime `vecmath`, `vecfp`, `vecint`, and workload methods verify that scalar fallbacks and vector paths both compile and run.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-vecmath.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-version.h -->
# sources/test-tools/stress-ng/core-version.h

## Purpose
`core-version.h` provides preprocessor helpers for comparing libc and compiler versions.

## Important APIs, Types, And Functions
`STRESS_VERSION_NUMBER` packs major, minor, and patchlevel into a comparable integer. `NEED_GLIBC`, `NEED_GNUC`, `EQUAL_GNUC`, `NEED_CLANG`, `NEED_ICC`, and `NEED_ICX` evaluate whether the active toolchain/runtime meets a requested version, or return 0 when version macros are unavailable.

## Control Flow
The file is entirely compile-time logic. Include sites use these macros to conditionally enable code paths, work around compiler bugs, or require minimum library versions.

## State And Persistence
No runtime state exists. The persistent effect is which code gets compiled for a given build environment.

## Dependencies And Integration Points
It depends on predefined compiler/libc macros such as `__GLIBC__`, `__GNUC__`, `__clang_major__`, `__INTEL_COMPILER`, and Intel LLVM macros. It integrates with portability gates throughout stress-ng.

## Risks
Version packing assumes minor and patch values fit the two-digit fields well enough for intended comparisons. The `NEED_ICX` macro compares packed requested versions against Intel's compiler version integer directly, which may not have the same encoding as `STRESS_VERSION_NUMBER`. Missing macros resolve to 0 and can silently disable code.

## Test Signals
Build matrix coverage across GCC, Clang, glibc, musl, and Intel compilers is the primary signal. Mis-gates appear as compile failures or missing optimized paths.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-vmstat.c -->
# sources/test-tools/stress-ng/core-vmstat.c

## Purpose
`core-vmstat.c` implements periodic runtime reporting for VM, CPU, thermal, I/O, status, and RAPL power statistics while stress-ng runs.

## Important APIs, Types, And Functions
The public functions are `stress_find_mount_dev`, `stress_vmstat_start`, and `stress_vmstat_stop`. Internal structures `stress_vmstat_t` and `stress_iostat_t` hold sampled counters. Platform-specific `stress_read_vmstat` implementations read Linux `/proc/stat`, `/proc/meminfo`, and `/proc/vmstat`, BSD sysctls, OpenBSD `sysctl`, or macOS Mach APIs. Linux I/O helpers include `stress_iostat_iostat_name`, `stress_read_iostat`, and `stress_iostat_get`. `stress_vmstat_get` converts absolute counters to deltas. `stress_tz_info_get` reads thermal-zone temperatures for periodic thermal output.

## Control Flow
`stress_vmstat_start` reads configured delays for `iostat`, `raplstat`, `status`, `thermalstat`, `vmstat`, and `vmstat-units`. If all are disabled it returns. Otherwise it forks a child named `stat [periodic]`, initializes baseline samples, optionally resolves a block-device stat path, and loops until the global continue flag clears. The loop advances scheduled wake times, sleeps with nanosecond precision, refreshes counters whose interval expired, and prints headers every 25 samples. `stress_vmstat_stop` kills and waits for the child.

## State And Persistence
Process state includes static delays, `vmstat_units_kb`, previous VM/I/O samples, and `vmstat_pid`. The child reads kernel-provided counters and shared stress-ng state such as instance counts, start time, thermal-zone list, and RAPL domains. It writes only log/stdout output, not project files.

## Dependencies And Integration Points
It depends on core CPU frequency, RAPL, thermal-zone, killpid, time, load-average, filesystem path, and platform sysctl/Mach/proc helpers. Command-line options `--vmstat`, `--iostat`, `--thermalstat`, `--status`, `--raplstat`, and `--vmstat-units` feed it. Debian fast tests run stressors with `--vmstat 1`; kernel coverage uses vmstat/iostat/thermal/RAPL paths extensively.

## Risks
This file is highly platform-conditional. Linux proc parsing assumes field order and units; block-device detection mutates the device string while stripping partition suffixes and can fail for device-mapper or unusual mounts. Forked reporter cleanup must be reliable. Static previous counters are not thread-safe but run in a dedicated process. Unit scaling guards only zero scale, not odd user input semantics.

## Test Signals
Runtime output under `--vmstat 1`, `--iostat 1`, `--thermalstat 1`, `--status 5`, and `--raplstat 1` is the main signal. Cross-platform builds validate alternate `stress_read_vmstat` implementations. Kernel coverage's broad filesystem and CPU runs exercise mount-device resolution and periodic formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-vmstat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-vmstat.h -->
# sources/test-tools/stress-ng/core-vmstat.h

## Purpose
`core-vmstat.h` exposes the VM/statistics reporter lifecycle and mount-device lookup API.

## Important APIs, Types, And Functions
It declares `stress_find_mount_dev`, `stress_vmstat_start`, and `stress_vmstat_stop`. The start/stop calls are used to manage the periodic stats child process.

## Control Flow
Callers start the stats reporter after options and shared state are initialized, then stop it during shutdown. `stress_find_mount_dev` can be called independently to map a path to its backing device.

## State And Persistence
The header declares no state. Implementation state includes reporter PID, delay settings, counter baselines, and output streams.

## Dependencies And Integration Points
It includes `core-attribute.h` for return attributes and relies on common declarations from the broader stress-ng include environment. It integrates with command-line option handling and global run lifecycle.

## Risks
Callers must avoid double-starting without stopping, because `core-vmstat.c` tracks only one static child PID. Device lookup returns static storage on supported platforms, so callers must copy results if they need stable values across later calls.

## Test Signals
Build coverage validates prototypes. Runtime validation comes from `--vmstat`, `--iostat`, and coverage-script runs that require the stats process to start and stop cleanly.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-vmstat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-workload.c -->
# sources/test-tools/stress-ng/core-workload.c

## Purpose
`core-workload.c` implements small synthetic work kernels used to waste a controlled amount of time with different CPU, memory, syscall, vector, and formatting behaviors.

## Important APIs, Types, And Functions
`workload_methods` maps method names to `STRESS_WORKLOAD_METHOD_*` IDs, and `stress_workload_method` returns names by index. The public `stress_workload_waste_time` runs one selected workload or randomized workloads until a time deadline. Internal methods include FMA arithmetic, NOP loops, architecture pause/yield instructions, process-name mutation, cache-flushing memory reads, string/number conversion, square-root/hypot math, integer vector math, and floating-point vector math.

## Control Flow
The dispatcher computes `t_end = stress_time_now() + run_duration_sec`, chooses a method (`all` chooses a random nonzero method once, while `random` chooses repeatedly), and loops until the deadline. Workloads consume buffers supplied by the caller for memory and formatting methods. Vector and FMA helpers are annotated with `TARGET_CLONES` when enabled so the compiler can dispatch optimized variants.

## State And Persistence
State is minimal but includes static counters in vector helpers and a static volatile `val` for increment workload. The process name workload persistently changes the running process name during execution. No files are written.

## Dependencies And Integration Points
It depends on architecture assembly helpers, CPU cache flushing, random number generation, safe memory/string shims, `core-target-clones.h`, `core-vecmath.h`, math library functions, and `stress_time_now`. The workload stressor and any scheduler/load simulation code can use the methods table for option parsing.

## Risks
`STRESS_WORKLOAD_METHOD_MAX` is currently defined as `STRESS_WORKLOAD_METHOD_VECFP`, excluding `VECINT` from random/all selection even though `VECINT` exists; this may be intentional or a coverage gap. Buffer length assumptions matter for `memmove(buffer, buffer + 1, buffer_len - 1)` and vector reads. Repeated `stress_time_now` calls use wall-clock time, so clock adjustments can affect run duration.

## Test Signals
The `workload` stressor and `kernel-coverage.sh` cases for workload schedulers, distributions, and thread counts exercise this file. Build coverage with and without vector math and target clones validates fallback paths.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-workload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-workload.h -->
# sources/test-tools/stress-ng/core-workload.h

## Purpose
`core-workload.h` defines workload method IDs, the method-name mapping type, and the public workload execution API.

## Important APIs, Types, And Functions
It defines IDs for `all`, `fma`, `getpid`, `inc64`, `memmove`, `memread`, `memset`, `mwc64`, `nop`, `pause`, `procname`, `random`, `strnum`, `sqrt`, `time`, `vecfp`, and `vecint`. `stress_workload_method_t` maps names to IDs. Exports are `workload_methods`, `stress_workload_method`, and `stress_workload_waste_time`.

## Control Flow
Option parsing can enumerate `workload_methods` or call `stress_workload_method`; runtime code calls `stress_workload_waste_time` with a method, duration, and scratch buffer.

## State And Persistence
No state is defined in the header. Implementation state includes small static counters and process-name changes for selected methods.

## Dependencies And Integration Points
It relies on common types such as `size_t` and `uint8_t`. The workload stressor and scheduler/load simulation code integrate with the method IDs.

## Risks
The `STRESS_WORKLOAD_METHOD_MAX` macro points to `VECFP` while `VECINT` has the next ID. Any code using max for enumeration or random selection may omit the last method unless it intentionally wants that behavior.

## Test Signals
Build coverage checks the declarations. Runtime `--workload` option tests and method enumeration validate name-to-ID consistency.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-workload.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/debian/rules -->
# sources/test-tools/stress-ng/debian/rules

## Purpose
`debian/rules` is the Debian package build driver for stress-ng.

## Important APIs, Types, And Functions
It is a debhelper makefile. It exports hardening build options, requests dpkg build flags and build tools, includes `/usr/share/dpkg/buildflags.mk` and `buildtools.mk`, overrides `dh_auto_build`, disables `dh_dwz`, and delegates all other targets to `dh`.

## Control Flow
For package builds, debhelper invokes this makefile. The build override exports shell-form dpkg build flags and calls `dh_auto_build`, passing `VERBOSE=1` unless `DEB_BUILD_OPTIONS` contains `terse`. The `override_dh_dwz` target is empty, so DWARF optimization is skipped.

## State And Persistence
It writes normal Debian package build artifacts through debhelper and the upstream build system. No runtime stress-ng state is touched.

## Dependencies And Integration Points
It depends on debhelper, dpkg build flags/tools infrastructure, and the upstream Makefile. Debian autopkgtests in `debian/tests` validate the built package.

## Risks
The `$(shell dpkg-buildflags --export=sh)` expression is expanded by make before the recipe line executes; changes to quoting can affect exported hardening flags. Disabling `dh_dwz` may be intentional to avoid debug-info issues, but it affects package size/debug optimization.

## Test Signals
Debian package build logs should show hardening flags and successful `dh_auto_build`. Autopkgtest scripts provide post-build runtime validation.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/debian/rules -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/debian/tests/fast-test-all -->
# sources/test-tools/stress-ng/debian/tests/fast-test-all

## Purpose
`debian/tests/fast-test-all` is an autopkgtest script that runs every built-in stressor briefly, excluding a small known-risk set, and summarizes pass/fail/skip counts.

## Important APIs, Types, And Functions
The script honors `STRESS_NG` or defaults to `stress-ng`, obtains stressor names with `--stressors`, defines `not_exclude`, and loops through stressors. Each included stressor runs as `${STRESS_NG} -v -t 1 --${s} 4 --verify --timestamp --metrics --vmstat 1`.

## Control Flow
The script prints system information, iterates discovered stressors, skips names in `EXCLUDE` (`l1cache` currently), runs each stressor, maps stress-ng exit codes 0 through 7 to pass/skip/fail categories, records names, and exits 1 if any stressor returns failure code 2.

## State And Persistence
It does not create intentional persistent files. Stressors under test may create temporary files or system effects according to their own cleanup. Output is the autopkgtest log.

## Dependencies And Integration Points
It depends on a runnable stress-ng binary in PATH or `STRESS_NG`, shell utilities, and stress-ng exit-code conventions. It directly exercises `core-stressors.h` registry output and reporting paths such as `core-vmstat.c`.

## Risks
Running every stressor can be noisy and environment-sensitive even with one-second duration. The unquoted `[ -z $STRESS_NG ]` test can misbehave when the variable contains whitespace or shell metacharacters. The script treats many abnormal returns as skipped, so only code 2 fails the test.

## Test Signals
Autopkgtest pass requires zero code-2 failures. Logs list passed, failed, and skipped stressor names, making registry or stressor-specific regressions visible.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/debian/tests/fast-test-all -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/debian/tests/lite-test -->
# sources/test-tools/stress-ng/debian/tests/lite-test

## Purpose
`debian/tests/lite-test` is a quicker autopkgtest smoke suite that runs a curated set of representative stressors for one second each.

## Important APIs, Types, And Functions
The script honors `STRESS_NG` or defaults to `stress-ng`, defines a fixed `STRESSORS` list including CPU, scheduler, data-structure, syscall, vector, and compression stressors, and runs `${STRESS_NG} -v -t 1 --${s} 4 --verify --timestamp` for each.

## Control Flow
It prints system information, iterates the fixed list, maps stress-ng exit codes to pass/fail/skip counters with the same convention as `fast-test-all`, records names, prints summary counts, and exits 1 only if a stressor returns code 2.

## State And Persistence
No intentional persistent state is created. Temporary files are managed by invoked stressors. Output is autopkgtest log text.

## Dependencies And Integration Points
It depends on shell, a runnable stress-ng binary, and stress-ng option/exit-code stability. The fixed list includes this subset's `af-alg` and many registry entries from `core-stressors.h`.

## Risks
The unquoted `[ -z $STRESS_NG ]` test is fragile. A fixed stressor list can lag renamed/removed stressors. Treating code 7 as a pass message but incrementing skipped count can make summary semantics confusing.

## Test Signals
A successful lite test has zero failures and reports pass/skip totals. It is a fast signal for broken binary startup, option parsing, and common stressor implementations.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/debian/tests/lite-test -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/kernel-coverage.sh -->
# sources/test-tools/stress-ng/kernel-coverage.sh

## Purpose
`kernel-coverage.sh` is a privileged, destructive-by-design kernel coverage harness that runs stress-ng workloads across schedulers, filesystems, I/O paths, memory controls, and stressor option combinations, then collects gcov/lcov reports.

## Important APIs, Types, And Functions
It defines `get_stress_ng_pids`, `kill_stress_ng`, `mount_filesystem`, `umount_filesystem`, `clear_journal`, and `do_stress`. It configures swap, perf permissions, core pattern, OOM score adjustment, lcov counters, branch tracing snapshots, many loop-mounted filesystems, scheduler and ionice sweeps, every discovered stressor, and a long list of stressor-specific option runs. It ends by collecting `kernel.info`, generating HTML, and converting HTML to text.

## Control Flow
The script validates `STRESS_NG`, derives stressor names from `--stressors` with `smi` removed, adjusts kernel tunables, creates a 2 GiB swap file, zeroes coverage counters, then runs staged workloads. Filesystem stages create images or special mounts, run I/O/filesystem stressors with several options and I/O schedulers, then unmount and clean. Later stages sweep schedulers, ionice classes, all stressors, and targeted option permutations. Cleanup restores swap, core pattern, perf paranoid, and generates coverage reports.

## State And Persistence
It writes `/tmp/swap.img`, `/tmp/fs.img`, `/tmp/sng-mnt-*` mount points, `/tmp/lower`, `/tmp/upper`, `/tmp/work` for overlay, local logs, `branch_all.start`, `branch_all.finish`, `kernel.info`, and `html/`. It writes kernel controls under `/proc/sys`, may load/unload modules such as nandsim/ubi/ubifs, changes I/O schedulers, mounts filesystems, vacuums journal logs, and runs stress-ng as root.

## Dependencies And Integration Points
It depends on bash, sudo, stress-ng, lcov/genhtml/html2text, mkfs tools for many filesystems, loop mounts, debugfs/gcov kernel configuration, `/sys/kernel/debug/tracing`, and numerous kernel features. It integrates directly with almost every stressor, `core-vmstat` status/iostat/thermal/RAPL paths, syslog/klog/perf reporting, and the stressor registry.

## Risks
This script is not a normal test; it mutates system-wide settings and can consume substantial CPU, memory, disk, and time. It uses unquoted variables in many places, assumes Linux root privileges, may leave mounts/images/modules if interrupted, and deliberately runs pathological stressors. Filesystem and kernel-feature assumptions can fail on minimal systems.

## Test Signals
Primary success signals are completed lcov/genhtml output and absence of unrecovered mounts or stuck stress-ng processes. Intermediate logs show each `STARTED`/`FINISHED` run, filesystem mount status, scheduler sweeps, and stressor return codes. Coverage growth in `kernel.info` is the intended output.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/kernel-coverage.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-access.c -->
# sources/test-tools/stress-ng/stress-access.c

## Purpose
`stress-access.c` implements the `access` stressor, exercising `access`, `faccessat`, `faccessat2`, `chmod`, and `fchmod` under concurrent permission changes.

## Important APIs, Types, And Functions
The stressor entry is `stress_access`, registered through `stress_access_info`. `stress_access_spawn` forks two lower-priority child loops that chmod and access a shared file. `stress_access_reap` kills/waits children. `shim_faccessat` prefers `faccessat2` or the raw syscall when available. Static `modes` maps chmod modes to access modes; `access_flags` probes multiple `faccessat` flags.

## Control Flow
The parent creates a temp directory and two files, mmaps shared PID records and metrics, spawns two child stressors, synchronizes start, and then loops over permission modes. For each mode it sets permissions, verifies expected access success or failure, exercises `faccessat` flags and bad descriptors, and increments bogo ops. Children concurrently mutate and query the second file, updating shared metrics. Cleanup kills children, restores file modes, closes/unlinks files, removes the temp directory, and unmaps shared memory.

## State And Persistence
Temporary filesystem state includes two files and a temp directory. Shared anonymous mmap state holds child PID records and metrics. The global static `metrics` pointer is used by children after fork. No persistent files should remain after normal cleanup.

## Dependencies And Integration Points
It depends on capability checks for root semantics, temp-file helpers, filesystem type detection, `core-sync`, `core-mmap`, `core-killpid`, and access/faccessat syscalls. It is registered as `CLASS_FILESYSTEM | CLASS_OS` with `VERIFY_ALWAYS`.

## Risks
Permission semantics vary by filesystem and root privileges; the code suppresses chmod/access failure reporting on exfat, msdos, hfs, and fuse. Concurrent chmod/access can race by design, so metrics and expected outcomes must be interpreted carefully. Child cleanup must run on all error paths to avoid leaked workers.

## Test Signals
`--access` with verification is a direct signal. Debian `fast-test-all` runs it, and kernel coverage exercises filesystem variants that can expose permission semantic differences.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-access.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-acct.c -->
# sources/test-tools/stress-ng/stress-acct.c

## Purpose
`stress-acct.c` implements the `acct` stressor, exercising Linux process accounting via `acct()` and reading generated accounting records.

## Important APIs, Types, And Functions
`stress_acct_supported` requires `CAP_SYS_PACCT`. `stress_acct` creates a temp accounting file, enables accounting with `acct(filename)`, forks/kills short-lived children, reads `struct acct_v3` records, increments bogo ops when records show `AXSIG`, truncates the file above 16 MiB, and disables accounting with `acct(NULL)`. `stress_acct_info` registers the stressor or an unimplemented stub depending on feature macros.

## Control Flow
After temp setup and sync-start wait, the loop checks file size, enables accounting, forks a child that exits immediately, kills/waits it from the parent, reads available accounting records from the file descriptor, validates accounting version once, then disables accounting. The loop continues while the stressor should run.

## State And Persistence
It creates a temporary accounting file and toggles system-wide process accounting to point at that file. It truncates the file to bound growth and removes it during cleanup. The accounting setting is intended to be disabled each iteration, but abnormal termination could leave accounting enabled until cleanup or external correction.

## Dependencies And Integration Points
It depends on Linux `acct`, `sys/acct.h`, `acct_v3`, `CAP_SYS_PACCT`, temp-file helpers, sync-start, kill/wait helpers, and file I/O shims. It is classified as `CLASS_OS` and `VERIFY_NONE` because support is privilege- and kernel-dependent.

## Risks
Process accounting is global, privileged state; running this stressor can interfere with other accounting users. The code reads from a descriptor after writes by the kernel; file offset behavior is important for seeing records. Feature guards limit implementation to Linux with v3 accounting support.

## Test Signals
Support checks should skip without `CAP_SYS_PACCT`. With privileges, bogo ops indicate accounting records with signal-exit flags were read. Failures show as `acct()` errors, unexpected accounting version warnings, or cleanup leaving accounting enabled.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-acct.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-acl.c -->
# sources/test-tools/stress-ng/stress-acl.c

## Purpose
`stress-acl.c` implements the `acl` stressor, generating and applying many valid POSIX ACL combinations to files and directories and verifying round-trip correctness.

## Important APIs, Types, And Functions
`stress_acl_setup` builds valid ACL objects from combinations of user/group/other permissions and ACL tags. `stress_acl_exercise` sets ACLs with `acl_set_file`, reads them back with `acl_get_file`, compares with `acl_cmp` or a text fallback, records metrics, and increments bogo ops. Helpers include `stress_acl_delete_all`, `stress_acl_perms`, and `stress_acl_free`. `stress_acl_info` registers options including `--acl-rand`.

## Control Flow
The stressor mmaps arrays for ACL handles and tested flags, generates valid ACLs, optionally randomizes order, creates a temp directory and file, synchronizes start, then repeatedly deletes existing ACLs and exercises both access and default ACL types where supported. It reports how many unique ACLs were tested and sets harmonic-mean nanosecond metrics for set/get operations before cleanup.

## State And Persistence
Runtime state includes heap/libacl ACL objects and mmap-backed arrays. Temporary filesystem state is a directory and file with ACL metadata that is deleted at cleanup. No persistent ACLs should remain.

## Dependencies And Integration Points
It requires libacl, `acl/libacl.h`, `sys/acl.h`, and non-static builds. It depends on temp path helpers, mmap helpers, sync-start, stress-ng metrics, and option parsing. Without support it registers `stress_unimplemented`.

## Risks
ACL semantics vary by filesystem, mount options, and Cygwin behavior; the code conditionally omits default ACLs or redundant group entries for those cases. The fallback comparison via `acl_to_text` assumes stable canonical text output. Large ACL generation can consume memory, so mmap failure is handled as no-resource.

## Test Signals
Direct `--acl` and `--acl-rand` runs validate generation, set/get, and comparison. Debian and kernel coverage include ACL runs, and filesystems without ACL support should return skip/not-implemented rather than hard failure.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-acl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-af-alg-defconfigs.h -->
# sources/test-tools/stress-ng/stress-af-alg-defconfigs.h

## Purpose
`stress-af-alg-defconfigs.h` provides a static catalog of Linux crypto algorithm configurations for the AF_ALG stressor to try even when modules are not yet listed in `/proc/crypto`.

## Important APIs, Types, And Functions
The file is an initializer fragment for `stress_crypto_info_t crypto_info_defconfigs[]`. Entries set fields such as `.crypto_type`, `.type`, `.name`, `.block_size`, `.max_key_size`, `.max_auth_size`, `.iv_size`, and `.digest_size` for AEAD, AHASH, AKCIPHER, CIPHER, RNG, SHASH, and SKCIPHER algorithms.

## Control Flow
It has no standalone control flow. `stress-af-alg.c` includes it inside an array initializer, then copies entries into the runtime crypto list via `stress_af_alg_add_crypto_defconfigs`.

## State And Persistence
The catalog is read-only compiled data. At runtime, entries are duplicated into heap-owned `stress_crypto_info_t` nodes with source `SOURCE_DEFCONFIG`.

## Dependencies And Integration Points
It depends on enum values and structure fields defined in `stress-af-alg.c`, so it is not a self-contained header. It integrates with AF_ALG bind attempts that can autoload crypto modules.

## Risks
Incorrect key, IV, digest, block, or auth sizes can cause false AF_ALG failures or skipped algorithms. Kernel crypto algorithm names change over time, and unsupported algorithms should be ignored cleanly. Because the file is included as an initializer, syntax errors break the parent C file.

## Test Signals
`--af-alg` and `--af-alg-dump` show whether defconfig entries are merged and exercised. Kernel coverage and lite autopkgtest include `af-alg`, providing broad smoke coverage on Linux systems with AF_ALG.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-af-alg-defconfigs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-af-alg.c -->
# sources/test-tools/stress-ng/stress-af-alg.c

## Purpose
`stress-af-alg.c` implements the `af-alg` stressor for Linux kernel crypto sockets, exercising hash, cipher/skcipher, AEAD, and RNG algorithms discovered from `/proc/crypto` plus built-in default configurations.

## Important APIs, Types, And Functions
The stressor uses `stress_crypto_type_t`, `stress_crypto_info_t`, and a linked `crypto_info_list`. Option handlers expose `--af-alg-dump` and `--af-alg-type`. Work functions include `stress_af_alg_hash`, `stress_af_alg_cipher`, `stress_af_alg_aead`, and `stress_af_alg_rng`. Discovery and list management include `name_to_type`, `type_to_type_string`, `stress_af_alg_count_crypto`, `stress_af_alg_sort_crypto`, `stress_af_alg_dump_crypto_list`, `dup_field`, `int_field`, `bool_field`, `stress_af_alg_add_crypto`, `stress_af_alg_add_crypto_defconfigs`, `stress_af_alg_init`, `stress_af_alg_deinit`, and `stress_af_alg_info_free`.

## Control Flow
Initialization parses `/proc/crypto` into crypto-info records, merges static defconfigs, sorts and optionally dumps the list. The stressor selects algorithms matching the requested type, opens AF_ALG sockets, binds by type/name, sets keys or auth sizes where needed, accepts operation sockets, sends random input through `send`, `sendmsg`, or reads RNG output, validates decrypt round-trips for ciphers, records per-algorithm metrics, and increments bogo ops. An alarm handler can longjmp out if an AF_ALG operation wedges after stop is requested.

## State And Persistence
Runtime state is the heap-owned crypto list, per-entry ignore/selftest flags and metrics, AF_ALG sockets, random buffers, signal jump state, and stress-ng bogo counters. It reads `/proc/crypto` and may trigger kernel module autoloading through bind. It does not write files.

## Dependencies And Integration Points
It requires Linux `AF_ALG`, `linux/if_alg.h`, `linux/socket.h`, socket APIs, crypto procfs format, random buffer helpers, sorting, metrics, and stress-ng signal handling. It is registered as `CLASS_CPU | CLASS_OS` with optional verification; unsupported builds expose `stress_unimplemented`.

## Risks
Kernel crypto providers vary widely; many bind, key, IV, auth-size, and selftest failures must be treated as skip/ignore rather than stressor failure. AF_ALG operations can hang or return surprising errno values, so alarm/longjmp cleanup is critical. Size fields are stored in small signed integer types, making catalog accuracy important.

## Test Signals
`--af-alg`, `--af-alg-type`, and `--af-alg-dump` are direct tests. Debian lite tests include `af-alg`; kernel coverage exercises it more heavily. Useful signals include successful algorithm count, skipped unsupported engines, no stuck sockets after SIGALRM, and nonzero per-algorithm operation metrics.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-af-alg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-affinity.c -->
# sources/test-tools/stress-ng/stress-affinity.c

## Purpose
`stress-affinity.c` implements the `affinity` stressor, rapidly changing CPU affinity across multiple processes to exercise scheduler affinity APIs and CPU mask behavior.

## Important APIs, Types, And Functions
`stress_affinity_info_t` is a shared control block containing CPU count, selected CPU, delay/sleep settings, random mode, and pin mode. `stress_affinity_supported` probes `sched_getaffinity`/`sched_setaffinity`. `stress_affinity_child` performs the affinity-change loop. `stress_affinity_reap` kills/waits helper children. `stress_affinity` orchestrates shared memory, locks, child forking, sync-start, and cleanup. `stress_affinity_info` registers options such as `--affinity-delay`, `--affinity-pin`, `--affinity-procs`, `--affinity-rand`, and `--affinity-sleep`.

## Control Flow
The main stressor determines child count, mmaps shared PID and info blocks, creates a counter lock, reads options, forks children into slots 1..N-1, synchronizes start, then runs `stress_affinity_child` in the parent as pin controller. Each loop chooses a CPU sequentially or randomly, optionally shares a pinned CPU through the control block, calls `sched_setaffinity`, verifies with `sched_getaffinity` when enabled, exercises invalid syscall arguments, increments bogo ops under a lock, and applies spin/sleep delays.

## State And Persistence
State is anonymous shared memory for PID records and affinity control plus a process-shared counter lock. It changes only process CPU affinity masks and does not persist filesystem state.

## Dependencies And Integration Points
It depends on Linux/BSD-style CPU affinity APIs, `cpu_set_t` macros, sync-start helpers, mmap helpers, kill/wait helpers, lock helpers, option settings, and stress-ng verification flags. It is classified as `CLASS_SCHEDULER`.

## Risks
CPU hotplug and restricted cpusets can make selected CPUs invalid; the loop handles `EINVAL` retry cases but verification can still be noisy under taskset-random/aggressive modes. `CPU_SET` is limited by `cpu_set_t` capacity, while `stress_cpus_configured_get` may exceed that on very large systems. Cleanup must reap many children reliably.

## Test Signals
Direct runs with `--affinity`, `--affinity-pin`, `--affinity-rand`, `--affinity-sleep`, and different `--affinity-procs` validate behavior. Kernel coverage includes affinity option sweeps, and support probing should skip on systems where affinity cannot be set.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-affinity.c -->
