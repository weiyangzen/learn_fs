# sources/distributed-fs/ceph-client/include/dt-bindings/clock/sifive-fu540-prci.h

## Purpose
`sifive-fu540-prci.h` defines device-tree clock indexes for the SiFive FU540 PRCI clock provider.

## Important APIs, types, and functions
The API consists of `FU540_PRCI_CLK_COREPLL`, `FU540_PRCI_CLK_DDRPLL`, `FU540_PRCI_CLK_GEMGXLPLL`, and `FU540_PRCI_CLK_TLCLK`. There are no functions or structs.

## Control flow
FU540 DTS nodes reference these IDs in clock specifiers. The PRCI driver maps each ID to the corresponding PLL or tile-link clock and implements rate/enable operations where supported.

## State and persistence
The header has no state. PRCI registers store actual PLL configuration and may be initialized by firmware before Linux takes ownership.

## Dependencies and integration points
It integrates with FU540 device trees, the SiFive PRCI driver, CPU/core clocking, DDR clocking, GEMGXL Ethernet clocking, and TLCLK consumers.

## Risks and test signals
Risks include renumbering the small ABI, requesting unsupported rate changes, and mismatches with firmware-initialized PLL state. Test signals include PRCI provider probe, CPU/DDR/Ethernet operation, clk-summary rates, and boot stability on HiFive Unleashed-class boards.
