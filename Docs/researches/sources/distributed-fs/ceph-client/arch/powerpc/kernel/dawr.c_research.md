<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/dawr.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/dawr.c

## Purpose
`dawr.c` manages PowerPC Data Address Watchpoint Register programming and the POWER9 debugfs override that can force-enable DAWR despite platform restrictions. It bridges generic hardware breakpoint requests to DAWR/DAWRX SPRs or platform callbacks.

## Important APIs, Types, And Functions
Exported global `dawr_force_enable` controls forced use. `set_dawr()` programs a DAWR slot from `struct arch_hw_breakpoint`. Helpers include `disable_dawrs_cb()`, `dawr_write_file_bool()`, `dawr_enable_fops`, and init function `dawr_force_setup()`.

## Control Flow
`set_dawr()` builds DAWRX bits from breakpoint read/write/translate/privilege type and doubleword-biased length, then delegates to `ppc_md.set_dawr()` if present or writes DAWR0/DAWR1 SPR pairs directly. The debugfs write path first validates that an LPAR hypervisor permits DAWR writes unless force-enable is already set, then updates the boolean and clears all DAWRs on all CPUs when disabling. Init auto-enables DAWR for CPUs with `CPU_FTR_DAWR`; POWER9 without that feature gets `dawr_enable_dangerous`.

## State And Persistence
Runtime state is the global boolean and per-CPU DAWR SPR contents. Debugfs changes are not persistent across reboot.

## Dependencies And Integration Points
It integrates with perf/hw-breakpoint code, platform machine descriptors, hypervisor calls, firmware feature detection, debugfs, CPU feature detection, and `nr_wp_slots()`.

## Risks
Forcing DAWR on restricted POWER9 systems can expose hardware errata or hypervisor denial behavior. Length encoding must handle zero or invalid lengths defensively through callers. Clearing DAWRs across CPUs is asynchronous with running debug users.

## Test Signals
Signals include hardware breakpoint tests, debugfs toggling on POWER9 LPARs, expected `-ENODEV` when the hypervisor rejects DAWR writes, and all watchpoint slots cleared after disabling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/dawr.c -->
