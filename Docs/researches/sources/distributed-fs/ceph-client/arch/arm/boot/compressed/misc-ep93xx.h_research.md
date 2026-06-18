<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/misc-ep93xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/boot/compressed/misc-ep93xx.h

## Purpose
This header provides declarations or platform-specific inline helpers for the ARM compressed boot environment, where normal kernel headers and drivers are not available.

## Important APIs, Types, and Functions
Declared or inline helpers include `Copyright`, `__raw_writeb`, `__raw_writel`, `ep93xx_ethernet_reset`, `ts72xx_watchdog_disable`, `ep93xx_decomp_setup`. Constants and guards include `PHYS_ETH_SELF_CTL`, `ETH_SELF_CTL_RESET`, `TS72XX_WDT_CONTROL_PHYS_BASE`, `TS72XX_WDT_FEED_PHYS_BASE`, `TS72XX_WDT_FEED_VAL`.

## Control Flow
The header is included by compressed boot C code. Inline helpers execute only if the including decompressor path calls them, typically before cache/MMU setup and before normal platform drivers exist.

## State and Persistence Behavior
State is limited to early MMIO side effects, decompressor globals, or declarations used by linked decompressor objects. Nothing is stored persistently, but early register writes can affect subsequent boot hardware state.

## Dependencies and Integration Points
Integration points include `misc.c`, `decompress.c`, platform-specific decompressor setup, low-level MMIO addresses, and the compressed linker/build rules.

## Risks
Risks are stale physical addresses, unavailable MMIO before the decompressor relocates, declaration mismatches across C/assembly boundaries, and hidden dependencies on bootloader-initialized hardware.

## Test Signals
Build the compressed boot configuration that includes this header and boot a target that exercises the helper. Inspect early boot output and hardware side effects such as watchdog disable or peripheral reset.

Source read size: 75 lines, 2004 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/boot/compressed/misc-ep93xx.h -->
