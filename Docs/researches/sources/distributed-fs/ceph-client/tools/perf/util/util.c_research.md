# sources/distributed-fs/ceph-client/tools/perf/util/util.c

## Purpose

`util.c` collects general perf utility functions for global mode flags, sysctl reads, perf attributes, directory creation/removal, CPU mask conversion, permissions, random tips, executable path discovery, debuginfod setup, chroot path expansion, dynamic array growth, and portability shims.

## Important APIs, Types, and Functions

Global state includes `input_name`, `perf_singlethreaded`, `sysctl_perf_event_max_stack`, `sysctl_perf_event_max_contexts_per_stack`, `exclude_GH_default`, `perf_host`, and `perf_guest`. Public functions include `perf_set_singlethreaded()`, `perf_set_multithreaded()`, `sysctl__max_stack()`, `sysctl__nmi_watchdog_enabled()`, `event_attr_init()`, `mkdir_p()`, `rm_rf_perf_data()`, `rm_rf()`, `lsdir_no_dot_filter()`, `lsdir()`, `cpumask_to_cpulist()`, `print_separator2()`, `hex_width()`, `perf_event_paranoid()`, `perf_event_paranoid_check()`, `perf_tip()`, `perf_exe()`, `perf_debuginfod_setup()`, `filename_with_chroot()`, `do_realloc_array_as_needed()`, compatibility `sched_getcpu()`, compatibility `scandirat()`, and `perf_basename()`.

## Control Flow and State

Sysctl helpers cache max stack/context settings and NMI watchdog status. `event_attr_init()` sets attr size and optional host/guest exclusion defaults. Recursive removal uses `lstat`, pattern matching, and depth limits; perf-data removal specially removes kcore directories only if their contents match expected names. CPU mask conversion parses hex blocks into a bitmap and formats a CPU list. Permission checks accept CAP_SYS_ADMIN, CAP_PERFMON, or a low enough `perf_event_paranoid`. Debuginfod setup clears or sets `DEBUGINFOD_URLS` based on CLI configuration and warns when support is not compiled in. Array growth doubles capacity with overflow checks and initializes new slots.

## Dependencies and Integration Points

It depends on procfs/sysctl helpers, capabilities, strlist/string helpers, bitmap formatting, Linux constants, perf debug logging, and libc filesystem APIs. It is widely used by command setup, cleanup, permission diagnostics, perf.data management, and UI output.

## State and Persistence Behavior

Some global booleans affect future event attribute initialization. Environment variable changes for debuginfod persist in the process. Filesystem helpers create or delete real paths; callers must ensure paths are safe.

## Risks and Test Signals

Risks include dangerous recursive deletion if callers pass wrong paths, pattern-removal partial failures, cpumask buffer assumptions, stale sysctl cache, environment side effects, lost old array pointer in `do_realloc_array_as_needed()` because it does not free the old array after copying, and portability syscall behavior. Tests should cover mkdir recursion, safe rm patterns, kcore cleanup constraints, cpumask conversions, permission checks under mocked sysctls/caps, debuginfod env modes, chroot filename generation, array growth initialization, and basename behavior.
