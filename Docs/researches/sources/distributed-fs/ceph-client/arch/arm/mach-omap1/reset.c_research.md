<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/reset.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/reset.c

## Purpose
Provides OMAP1 restart and last-reset-source decoding for reboot and watchdog integration.

## Important APIs, Types, and Functions
Defines `omap1_restart(enum reboot_mode, const char *)` and `omap1_get_reset_sources()`.

## Control Flow
Restart applies an OMAP5912/1611B workaround by disabling a DPLL control bit and writing `ARM_RSTCT1`, then triggers global software reset. Reset-source decoding reads `ARM_SYSST` and maps POR, external reset, ARM watchdog, and global software reset bits into standardized OMAP reset-source IDs.

## State and Persistence Behavior
No persistent software state. It writes reset control registers and reads retained reset status bits.

## Dependencies and Integration Points
Depends on OMAP1 hardware register definitions, `omap_readw/writew`, `OMAP1_IO_ADDRESS`, common CPU predicates, and reboot/watchdog consumers.

## Risks
Restart is final and does not return. The OMAP5912 workaround affects traffic-controller frequency behavior and must happen before reset. Reset-source mapping depends on ARM_SYSST bit definitions.

## Test Signals
Trigger cold, warm, watchdog, and external resets where possible and verify watchdog-reported reset-source bits. Reboot OMAP5912-class hardware repeatedly to check the workaround avoids bad post-reset frequency state.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/reset.c -->
