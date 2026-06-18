# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igbvf/regs.h

## Purpose
`regs.h` defines the VF-visible Intel register map and MMIO access macros used by `igbvf`.

## Important APIs, Types, And Functions
The file defines offsets for control/status, interrupt registers, IVAR, queue descriptor registers, DCA controls, receive address registers, VF statistics, V2P mailbox, and mailbox memory. Queue register macros such as `E1000_RDBAL(_n)`, `E1000_RDLEN(_n)`, `E1000_RXDCTL(_n)`, `E1000_TDBAL(_n)`, and `E1000_TXDCTL(_n)` encode hardware's split register layout for queues below and above index 4. Access macros `er32`, `ew32`, `array_er32`, `array_ew32`, and `e1e_flush()` wrap `readl()`/`writel()`.

## Control Flow
There is no executable control flow. These macros are invoked throughout `netdev.c`, `vf.c`, `mbx.c`, and `ethtool.c` for hardware access.

## State And Persistence
No software state is stored. The macros read and write MMIO-backed device state through `hw->hw_addr`.

## Dependencies And Integration Points
The macros assume the local variable name `hw` points to `struct e1000_hw`. This convention is used throughout the driver. Register offsets integrate the VF network path, interrupts, stats, and mailbox protocol with hardware.

## Risks
The `hw` implicit-variable style is concise but fragile during refactors. Incorrect offsets can corrupt hardware state or access the wrong queue. Register reads can have side effects, especially interrupt and mailbox status registers. Queue macro layout must match supported VF devices.

## Test Signals
Build tests catch missing register macros. Runtime validation includes ethtool register dump, interrupt delivery, ring enable/disable, mailbox communication, VF stats reads, and successful packet I/O.
