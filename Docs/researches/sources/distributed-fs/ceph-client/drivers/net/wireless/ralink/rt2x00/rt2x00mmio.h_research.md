# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00mmio.h

## Purpose
`rt2x00mmio.h` declares the MMIO transport interface and provides inline register accessors for rt2x00 memory-mapped devices. It is the contract used by PCI-style hardware drivers to read and write CSR space, allocate per-entry descriptor state, and call shared MMIO queue/lifecycle helpers.

## Important APIs, Types, And Functions
Inline functions `rt2x00mmio_register_read()`, `rt2x00mmio_register_multiread()`, `rt2x00mmio_register_write()`, and `rt2x00mmio_register_multiwrite()` wrap `readl()`, `memcpy_fromio()`, `writel()`, and `__iowrite32_copy()` against `rt2x00dev->csr.base + offset`. The header declares `rt2x00mmio_regbusy_read()`, `rt2x00mmio_rxdone()`, `rt2x00mmio_flush_queue()`, `rt2x00mmio_initialize()`, and `rt2x00mmio_uninitialize()`. `struct queue_entry_priv_mmio` stores a descriptor pointer and DMA address for each queue entry.

## Control Flow
Hardware drivers include this header to perform direct CSR access and to provide shared transport callbacks in `struct rt2x00lib_ops`. Typical flow is PCI probe maps BAR0 into `rt2x00dev->csr.base`, queue allocation assigns `priv_size = sizeof(struct queue_entry_priv_mmio)`, MMIO initialization fills each private descriptor pointer, and hardware init programs ring base registers from `desc_dma`.

## State And Persistence
The header does not own state by itself. Its accessors operate on the mapped CSR base owned by the PCI probe path. `queue_entry_priv_mmio` is persistent for the lifetime of queue entries and points into coherent DMA descriptor memory allocated by `rt2x00mmio.c`.

## Dependencies And Integration Points
It depends on Linux I/O helpers and rt2x00 core definitions. The accessors are used heavily by chip drivers such as `rt61pci.c` for register, BBP, RF, EEPROM, queue, interrupt, and power-state programming.

## Risks
The inline register functions perform no bounds checks on offsets or lengths. Multiwrite assumes the length is a multiple of four because it shifts by two for `__iowrite32_copy()`. Consumers must ensure `csr.base` is valid and device presence is checked at the call site where necessary. Descriptor DMA addresses must fit the hardware programming model.

## Test Signals
Signals are compile coverage for all MMIO users, successful CSR reads/writes during probe, ring-base programming matching `queue_entry_priv_mmio.desc_dma`, and no sparse/endian warnings around descriptor and register access.
