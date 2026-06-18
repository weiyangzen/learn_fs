<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap54xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap54xx.h

## Purpose
`omap54xx.h` defines OMAP5 and DRA7 base addresses for interconnects, PRCM/control, SAR RAM, and DRA7-specific L3/L4/PRCM/TAP regions.

## Important APIs, Types, and Functions
OMAP5 constants include `L4_54XX_BASE`, `L4_WK_54XX_BASE`, `L4_PER_54XX_BASE`, `L3_54XX_BASE`, `OMAP54XX_32KSYNCT_BASE`, CM/PRM/PRCM MPU bases, SCM/control bases, and `OMAP54XX_SAR_RAM_BASE`. DRA7 constants include L3 main, L4 PER/CFG/WKUP bases, `DRA7XX_CM_CORE_AON_BASE`, `DRA7XX_CTRL_BASE`, and `DRA7XX_TAP_BASE`.

## Control Flow
No runtime control flow exists. The constants are consumed by IO mapping and early platform setup.

## State and Persistence Behavior
No state is stored; this is a fixed hardware address map.

## Dependencies and Integration Points
It integrates with `iomap.h`, `io.c`, OMAP5/DRA7 PRCM/control setup, SAR low-power code, and revision detection through DRA7 TAP base.

## Risks
The closing comment has a typo in the guard name, but the actual guard macro is consistent. Wrong DRA7 mapping bases can break early boot because DRA7 has multiple L4 peripheral windows and address holes.

## Test Signals
Compile and boot OMAP543x and DRA7xx configs. Validate PRCM/control/TAP access, SAR mapping, GIC/WakeupGen, and peripheral probes under all DRA7 L4 windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap54xx.h -->
