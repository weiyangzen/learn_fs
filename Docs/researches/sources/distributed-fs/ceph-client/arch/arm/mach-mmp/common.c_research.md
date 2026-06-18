# sources/distributed-fs/ceph-client/arch/arm/mach-mmp/common.c

Purpose: Common MMP/PXA static IO mapping and chip-id discovery.

Important APIs/types/functions: Defines exported `mmp_chip_id`, `mmp_map_io()`, and `mmp2_map_io()`.

Control flow: `mmp_map_io()` maps APB and AXI register windows with `iotable_init()` and immediately reads `MMP_CHIPID` from the CIU register into exported `mmp_chip_id`. `mmp2_map_io()` extends that setup by mapping the PGU/SCU window used by MMP2/MMP3-class cores.

State and persistence: Persistent kernel state is exported `mmp_chip_id`. Static hardware mappings cover APB, AXI, and optionally PGU/SCU device ranges.

Dependencies and integration points: Depends on `addr-map.h`, ARM static mapping, raw MMIO reads, and CPU type helpers consuming the chip id.

Risks: The chip-id read requires AXI mapping to be valid and happens very early. Wrong mapping constants affect every early MMP register access. There is no runtime DT resource validation for these static windows.

Test signals: Boot PXA168/PXA910/MMP2/MMP3 DT machines, verify chip-id-based CPU detection, and test early timer/clock code that uses APB/AXI mappings.
