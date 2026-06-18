# sources/distributed-fs/ceph-client/drivers/net/ethernet/seeq/sgiseeq.h

Purpose: Defines SGI Seeq8003 register layouts and status/command/control bits used by the SGI HPC3-backed driver.

Important APIs and types: `struct sgiseeq_regs` models banked Seeq registers for station address, multicast bytes, write-side controls, read-side collision/status counters, receive status, and transmit status. Macros define receive status bits, receive command bits, transmit status bits, transmit command bits, Seeq control flags, and SGI Hollywood HPC PIO/DMA/control timing/reset/IRQ flags.

State and dependencies: The header has no runtime state but forms the MMIO layout contract for `sgiseeq.c`. It also mirrors HPC integration bits that must match SGI platform hardware headers.

Risks and test signals: Bit definitions must align with hardware and with `sgiseeq.c` error handling; mistakes can invert receive mode, miss interrupts, or mishandle reset. Tests should include compile coverage on SGI_HAS_SEEQ, register-bank selection for MAC/multicast programming, receive status error accounting, and EDLC control programming.
