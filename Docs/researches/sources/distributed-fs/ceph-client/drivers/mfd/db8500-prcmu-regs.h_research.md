# sources/distributed-fs/ceph-client/drivers/mfd/db8500-prcmu-regs.h

## Purpose
`db8500-prcmu-regs.h` defines the DB8500 PRCMU register offsets and bit fields used by the PRCMU implementation. It is a hardware contract header for clock, PLL, mailbox, reset, clamp, semaphore, timer, GPIO, and power-management registers.

## Important APIs, Types, and Functions
The header provides the `BITS(_start, _end)` mask helper and many `PRCM_*` macros. Key groups include clock-management offsets such as `PRCM_UARTCLK_MGT`, ARM PLL/divider registers, mailbox CPU set/clear/value registers, interrupt status/clear/mask registers, PLLSOC/PLLDSI frequency fields, DSI clock divider fields, clock output fields, ePOD/memory power registers, hardware semaphore `PRCM_SEM`, timer control `PRCM_TCR`, GPIO routing bits, and reset registers.

## Control Flow
There is no executable control flow. The implementation includes this header and combines offsets with the global `prcmu_base` pointer for MMIO reads and writes.

## State and Persistence
The macros describe volatile PRCMU MMIO state. Persistence depends entirely on SoC reset and power-domain behavior; this header stores no state.

## Dependencies and Integration Points
The header assumes Linux `BIT()` is available and that `prcmu_base` is visible in the including C file for address-valued macros. It is tightly coupled to `db8500-prcmu.c` rather than a standalone generic header.

## Risks and Edge Cases
Many macros expand to pointer expressions using `prcmu_base`, so they cannot be safely used before the base is mapped. `PRCM_APE_SOFTRST` is defined twice with the same value. Register fields are SoC-specific; reuse for DB8520/U8540-style variants must be checked against hardware documentation.

## Test Signals
Validation signals are compile success after inclusion, correct MMIO addresses in early boot traces, expected clock/PLL bit manipulation, mailbox interrupt clear behavior, and no use before `prcmu_base` initialization.
