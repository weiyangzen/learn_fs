<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap4-restart.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap4-restart.c

## Purpose
`omap4-restart.c` implements the common OMAP4/OMAP5 restart hook using PRM system reset.

## Important APIs, Types, and Functions
The public function is `omap44xx_restart(enum reboot_mode mode, const char *cmd)`.

## Control Flow
The restart hook ignores `mode` and `cmd` except for a comment noting that `cmd` could be saved to scratchpad later. It calls `omap_prm_reset_system()` and expects hardware reset.

## State and Persistence Behavior
No local state is stored. The only state transition is PRM reset hardware state; reboot command persistence is not implemented.

## Dependencies and Integration Points
It depends on reboot type definitions and `prm.h`. It integrates as the machine restart callback for OMAP4/5-like systems.

## Risks
If PRM reset fails, restart returns unexpectedly. Not preserving `cmd` means bootloader-specific reboot modes are unavailable through this path.

## Test Signals
Run `reboot` on OMAP4/OMAP5/DRA7 systems using this hook and confirm immediate SoC reset. Test reboot command variants if platform firmware expects scratchpad data and verify they are not accidentally relied upon.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap4-restart.c -->
