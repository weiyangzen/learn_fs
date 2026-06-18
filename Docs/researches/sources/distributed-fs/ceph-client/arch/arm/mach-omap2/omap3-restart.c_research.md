<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap3-restart.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap3-restart.c

## Purpose
`omap3-restart.c` implements OMAP3 software restart through the PRM reset path and optional scratchpad boot-mode communication.

## Important APIs, Types, and Functions
The public function is `omap3xxx_restart(enum reboot_mode mode, const char *cmd)`.

## Control Flow
On restart, the function may interpret or pass restart mode information through OMAP3 control scratchpad helpers, then calls `omap_prm_reset_system()` to trigger SoC reset. Like other restart hooks, it is expected not to return.

## State and Persistence Behavior
State is limited to scratchpad boot-mode data and PRM reset hardware state. No filesystem persistence exists.

## Dependencies and Integration Points
It depends on reboot core, PRM reset functions, and OMAP3 control scratchpad helper declarations. It integrates as the machine restart callback for OMAP3-class SoCs.

## Risks
If scratchpad values are wrong, bootloader or ROM-visible reboot mode can be miscommunicated. If PRM reset fails, the system remains running after a restart request.

## Test Signals
Run reboot on OMAP3 boards with normal and bootloader-specific reboot commands if supported. Confirm reset occurs and any boot-mode scratchpad behavior is interpreted by downstream firmware as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap3-restart.c -->
