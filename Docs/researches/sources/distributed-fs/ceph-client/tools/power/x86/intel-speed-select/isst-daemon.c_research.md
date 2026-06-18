# sources/distributed-fs/ceph-client/tools/power/x86/intel-speed-select/isst-daemon.c

## Purpose
`isst-daemon.c` implements the OOB daemon/polling support for `intel-speed-select`. Its job is to detect performance-level changes made by an out-of-band agent and apply matching CPU online/offline or cgroup isolation changes so the OS CPU availability matches the active SST performance profile.

## Important APIs, Types, And Functions
The exported functions are `isst_daemon()` and `process_level_change()`. Internal state is stored in `per_package_levels_info[MAX_PACKAGE_COUNT][MAX_DIE_PER_PACKAGE][MAX_PUNIT_PER_DIE]` and matching timestamp array `per_package_levels_tm`. `init_levels()` initializes level state to `-1`. `poll_for_config_change()` iterates online power domains through `for_each_online_power_domain_in_set()`. `daemonize()` performs fork/session setup, PID file creation, and lock acquisition. `signal_handler()` exits and calls `hfi_exit()`.

## Control Flow
`isst_daemon()` installs signals or daemonizes depending on flags, initializes remembered levels, and chooses between HFI event mode and polling mode. If no poll interval is supplied, it calls `hfi_main()` and returns an error message instructing the user to specify a poll interval. In poll mode it sleeps for `poll_interval` seconds and calls `poll_for_config_change()` until termination. Each power domain enters `process_level_change()`, which rate-limits checks to at most once every two seconds per package/die/punit, reads current TDP level, ignores locked configs and unchanged levels, fetches the core mask for the current level, and then either isolates non-enabled CPUs with cgroup v2 or hotplugs CPUs online/offline through sysfs.

## State And Persistence Behavior
Process state tracks the last observed level and last check timestamp per power domain. Persistent host effects include PID file `/tmp/hfi-events.pid`, daemon working directory `/tmp/`, optional cgroup v2 partition changes, and CPU hotplug writes through `set_cpu_online_offline()`. The signal handler sets `done` but also exits immediately for SIGINT/SIGTERM after `hfi_exit()`.

## Dependencies And Integration Points
This file depends heavily on APIs exported by `isst-config.c` and `isst-core.c`: topology iteration, current-level reads, core-mask reads, cgroup helpers, and CPU online/offline writes. It also integrates with `hfi-events.c` via `hfi_main()` and `hfi_exit()`. It shares all hardware/backend dependencies of the selected platform ops.

## Risks And Edge Cases
Running as a daemon can close standard file descriptors before later code writes diagnostics. `daemonize()` uses a single PID file path and lock, so concurrent daemons should fail but stale lock behavior depends on OS cleanup. The level timestamp array prevents rapid repeated work but may also suppress legitimate quick changes. `process_level_change()` assumes `pkg`, `die`, and `punit` are valid array indexes. CPU hotplug and cgroup operations can disrupt workloads and require root. HFI mode currently reports that a poll interval must be specified after trying `hfi_main()`.

## Test Signals
Tests should cover initial level tracking, unchanged-level no-op behavior, locked-config no-op behavior, poll loop dispatch, cgroup fallback to hotplug, signal handling, PID lock contention, and rate limiting. On real hardware, observe that changing SST level causes the enabled core mask to be applied exactly once per level change.
