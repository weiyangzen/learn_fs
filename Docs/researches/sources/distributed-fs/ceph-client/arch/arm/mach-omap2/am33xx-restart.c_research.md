<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/am33xx-restart.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/am33xx-restart.c

## Purpose
Implements AM33xx restart behavior, including a pinmux workaround for Advisory 1.0.36 before issuing a PRM system reset.

## Important APIs, Types, and Functions
Defines `am33xx_restart(enum reboot_mode, const char *)` and internal `am33xx_advisory_1_0_36()`.

## Control Flow
Restart first reads EMU0/EMU1 pin control registers. If either pin is not in EMU mode, it clears the mux mode bits to switch GPIO3_7/GPIO3_8 back to EMU inputs, delays 5 ms for pull-ups, stores reboot mode in `prm_reboot_mode`, and calls `omap_prm_reset_system()`.

## State and Persistence Behavior
Persistent hardware state before reset is the EMU pin mux mode. Software state is `prm_reboot_mode`, consumed by PRM reset handling.

## Dependencies and Integration Points
Depends on AM335x pinctrl register offsets, control-module read/write helpers, PRM reset APIs, and `mdelay()`.

## Risks
If EMU pins are driven low as GPIO outputs at reset sampling, the SoC may reboot into the wrong mode; this workaround must run very late and quickly. It cannot fully control external board pull-ups.

## Test Signals
Reboot AM33xx systems with EMU pins previously muxed as GPIO low/high and verify normal boot mode. Confirm `reboot_mode` reports warm behavior from board-generic machine descriptor.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/am33xx-restart.c -->
