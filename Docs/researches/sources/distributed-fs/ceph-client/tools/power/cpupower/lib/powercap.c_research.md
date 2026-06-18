# sources/distributed-fs/ceph-client/tools/power/cpupower/lib/powercap.c

## Purpose
Implements the cpupower powercap/RAPL library layer. It discovers the intel-rapl powercap hierarchy under `/sys/devices/virtual/powercap`, reads zone names and capability flags, exposes energy/power counters, and provides a recursive walker used by both `powercap-info` and the RAPL monitor.

## Important APIs, Types, and Functions
Key entry points are `powercap_get_enabled`, `powercap_get_driver`, `powercap_init_zones`, `powercap_read_zone`, `powercap_walk_zones`, and the 64-bit readers `powercap_get_energy_uj`, `powercap_get_power_uw`, `powercap_get_max_energy_range_uj`, and `powercap_get_max_power_range_uw`. Internal helpers `sysfs_read_file`, `sysfs_get_enabled`, and `sysfs_powercap_get64_val` hide low-level open/read parsing.

## Control Flow, State, and Persistence
`powercap_init_zones` first requires `/intel-rapl/enabled` to read as enabled, allocates a root `powercap_zone`, seeds `sys_name` as `intel-rapl/intel-rapl:0`, and calls `powercap_read_zone`. `powercap_read_zone` opens the zone directory, reads its `name`, marks whether energy/power files can be read, scans child `intel-rapl:*` directories, allocates child structs, links parent/children pointers, and recurses with tree depth tracking. State is entirely live sysfs data plus heap-allocated zone trees; no persistent storage is written. `powercap_set_enabled` and `powercap_zone_set_enabled` are stubs returning success without writing sysfs.

## Dependencies and Integration Points
Depends on Linux powercap sysfs, the `powercap.h` struct contract, libc directory/stat APIs, and callers in `utils/powercap-info.c` and `utils/idle_monitor/rapl_monitor.c`. The code is intentionally hardwired to intel-rapl even though powercap is a generic kernel class.

## Risks and Test Signals
Path construction uses fixed 255-byte buffers with unchecked `strcat` in several places, so deep or unexpected sysfs names could overflow despite some checks. `stat(dent->d_name)` is relative to cwd before falling back to `fstatat`, which is harmless but odd. Child allocation failures can leak already-built subtrees, and no destructor is provided. Validate with systems where RAPL is enabled/disabled, nested package/core/uncore zones, missing energy files, artificially long names, and `cpupower powercap-info` plus `cpupower monitor -m RAPL` smoke tests.
