## sources/distributed-fs/ceph-client/drivers/net/ethernet/apple/bmac.h

Purpose: register map and bit definitions for the Apple Big MAC controller used by `bmac.c`.

Important APIs/types: this header exports preprocessor constants only. It defines offsets for global interface registers (`XIFC`, `MIFCSR`, `SROMCSR`, `STATUS`, `INTDISABLE`), FIFO controls, TX registers (`TXRST`, `TXCFG`, collision counters), RX registers (`RXRST`, `RXCFG`, receive counters), multicast hash registers, MAC address registers, and error/interrupt masks.

Control flow: no executable control flow. The runtime driver uses these constants to reset TX/RX paths, program station address words, configure multicast hash filters, enable/disable interrupts, interpret error bits, and drive PHY/SROM sideband registers.

State and persistence: no state is stored here; it describes hardware state held in BMAC registers. Some masks are shared between status and interrupt-disable semantics, which is important because reads of `STATUS` clear latched conditions.

Dependencies/integration: consumed directly by `bmac.c`; comments note similarity to Sun HME. The register values assume the MMIO layout used by Apple macio BMAC hardware.

Risks: incorrect bit polarity can be serious because `INTDISABLE` uses disable-mask style values while `STATUS` uses event bits. Multiword MAC address register ordering must match the driver’s word writes. Header naming includes legacy/uncertain comments for some registers, so changes should be hardware-validated.

Test signals: compile coverage through `bmac.c`; runtime validation through successful reset, interrupt enable/disable behavior, multicast filtering, and accurate statistics counter increments.
