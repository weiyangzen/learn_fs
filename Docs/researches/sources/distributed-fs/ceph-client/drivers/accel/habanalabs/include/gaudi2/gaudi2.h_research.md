# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/gaudi2.h

## Purpose
`gaudi2.h` provides shared Gaudi2 constants for BAR IDs/sizes, physical and virtual address ranges, memory sizes, interrupt counts, queue-entry sizing, ASID limits, ARC counts, engine topology, and cache-line size.

## Important APIs, Types, And Functions
The header exports macros for SRAM/MSIX/DRAM BAR IDs and sizes, CFG base/size/region size, STM/SPI flash, scratchpad SRAM, PCIe firmware SRAM, BAR0 reserved window, SRAM and DRAM physical bases, DRAM VA hint mask, host physical windows, reserved virtual ranges for ARC on HBM/host and virtual MSI-X doorbells, the unexpected user-error MSI-X index, `GAUDI2_MSIX_ENTRIES`, QMAN PQ entry size, `MAX_ASID`, ARC CPU and DCCM details, DCORE and per-engine instance counts, TPC tensor counts, MME seed count, NIC macro/engine/port counts, and `DEVICE_CACHE_LINE_SIZE`.

## Control Flow
There is no executable flow. These constants parameterize driver initialization, memory mapping, queue sizing, interrupt allocation, topology iteration, virtual address reservation, and engine enumeration.

## State, Persistence, And Dependencies
The header stores no state. It is a central compile-time contract that must match silicon, firmware, generated register maps, and user-visible driver capabilities. Derived constants such as NIC engine/port counts build on base topology macros.

## Integration Points
The file is included by Gaudi2 driver code and aligns with generated register headers, async event IDs, queue-manager setup, MMU/VA management, MSI-X setup, ARC firmware loading, and engine discovery.

## Risks
Incorrect constants can cause invalid BAR mappings, memory-window overlap, queue mis-sizing, missing interrupts, wrong engine loops, or security holes in reserved VA regions. `MAX_ASID` and address masks are especially sensitive for isolation and MMU behavior.

## Test Signals
Signals include successful PCI BAR discovery, MMIO and DRAM mapping, correct MSI-X count, all expected engines enumerated exactly once, valid reserved VA allocation, queue entry alignment, ARC DCCM access, and NIC/TPC/MME counts matching firmware reports.
