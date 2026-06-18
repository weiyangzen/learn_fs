# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/powercap-info.c

## Purpose
Implements `cpupower powercap-info`, printing the loaded powercap driver and intel-rapl zone hierarchy with enabled state and available monitoring capabilities.

## Important APIs, Types, and Functions
Important functions are `powercap_print_one_zone`, `powercap_show`, `cmd_cap_info`, and placeholder `cmd_cap_set`. Option `--all` sets global `powercap_show_all`, but the current printer does not branch on it.

## Control Flow, State, and Persistence
`cmd_cap_info` parses options, then `powercap_show` checks driver and global enabled state, initializes the zone tree, and walks it printing each zone with indentation derived from tree depth. The command reads sysfs only. `cmd_cap_set` is a no-op returning success.

## Dependencies and Integration Points
Depends on `lib/powercap.c`, `powercap.h`, helper gettext macros, and cpupower dispatch. Integrates with RAPL monitor through the same zone discovery API.

## Risks and Test Signals
The printed string says energy is monitored in micro Joules as "Power", which is imprecise. No memory is freed for the zone tree. `--all` and cap set are not functional. Test no driver, disabled powercap, zones without enabled files, nested zones, and command output under non-root users.
