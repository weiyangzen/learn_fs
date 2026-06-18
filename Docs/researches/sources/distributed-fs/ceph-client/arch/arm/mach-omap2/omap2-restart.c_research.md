<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap2-restart.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap2-restart.c

## Purpose
`omap2-restart.c` implements OMAP2xxx software restart by temporarily reparenting/resetting PRCM clocks and waiting for reset to occur.

## Important APIs, Types, and Functions
The public restart function is `omap2xxx_restart(enum reboot_mode mode, const char *cmd)`. Internal state includes `reset_virt_prcm_set_ck` and `reset_sys_ck`. The init helper `omap2xxx_common_look_up_clks_for_reset()` runs as an initcall to cache clock handles.

## Control Flow
The init helper looks up clocks needed for reset. The restart function programs the reset clock path, invokes PRCM reset behavior, then loops waiting for hardware reset. The `cmd` parameter is not persisted.

## State and Persistence Behavior
State is cached clock pointers and PRCM reset hardware state. No filesystem persistence exists; successful operation terminates the running kernel via SoC reset.

## Dependencies and Integration Points
It depends on clock framework, PRM/CM reset helpers, reboot core, and OMAP2xxx clock names. It is registered as the machine restart callback for OMAP2xxx platforms.

## Risks
Missing clock lookup or wrong clock parent prevents reset. Since restart should not return, any failure leaves the system running in a partially modified clock state. Lack of scratchpad `cmd` persistence means reboot mode strings are ignored.

## Test Signals
On OMAP2xxx hardware, run `reboot`, watchdog-adjacent reset tests, and verify the system resets promptly. Check boot logs for clock lookup failures and confirm reset path does not return.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap2-restart.c -->
