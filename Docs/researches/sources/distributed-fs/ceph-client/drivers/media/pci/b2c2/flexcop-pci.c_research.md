# sources/distributed-fs/ceph-client/drivers/media/pci/b2c2/flexcop-pci.c

## Purpose
`flexcop-pci.c` is the PCI bus driver for B2C2 FlexCop digital TV devices. It maps the PCI register window, wires the generic FlexCop core to PCI register accessors, allocates DMA buffers, services DMA/timer interrupts, and feeds MPEG transport stream data into the DVB demux.

## Important APIs, Types, and Functions
`struct flexcop_pci` stores the PCI device, init-state flags, MMIO mapping, two DMA descriptors, active DMA page, streaming counters, IRQ lock, delayed watchdog work, and the owning `struct flexcop_device`. Core functions include `flexcop_pci_read_ibi_reg()`, `flexcop_pci_write_ibi_reg()`, `flexcop_pci_isr()`, `flexcop_pci_stream_control()`, `flexcop_pci_dma_init()`, `flexcop_pci_dma_exit()`, `flexcop_pci_init()`, `flexcop_pci_exit()`, `flexcop_pci_probe()`, and `flexcop_pci_remove()`.

## Control Flow
Probe allocates a FlexCop core object with bus-private storage, installs PCI register and bus callbacks, applies module parameters for PID filtering and debug, enables the PCI device, maps BAR0, requests the shared IRQ, initializes the FlexCop core, allocates DMA1 and DMA2 buffers, routes SRAM destinations to those DMAs, and optionally schedules the IRQ watchdog. Stream start configures both DMA engines, configures the DMA1 timer, starts both DMA1 subaddresses, resets the last cursor, and enables DMA1 timer IRQs. The ISR reads `irq_20c`, logs error bits, then either passes a completed DMA page on page-change IRQ or computes the current DMA cursor on timer IRQ and feeds newly written byte ranges, including wraparound handling. Stream stop disables timer IRQs and stops DMA1 transfers. Remove cancels watchdog work, frees DMA memory, shuts down the core, releases PCI resources, and frees the core object.

## State and Persistence
Runtime state lives in `struct flexcop_pci`: initialization flags gate cleanup, `active_dma1_addr` selects the next page-buffer half, `last_dma1_cur_pos` tracks streaming progress for timer mode, and watchdog counters detect stalled IRQs. Hardware state is PCI BAR MMIO and DMA engine registers. No state is persisted beyond the lifetime of the device.

## Dependencies and Integration Points
The driver integrates with PCI core via `module_pci_driver()`, the FlexCop common core via `flexcop_device_initialize()`/`exit()` and callback fields, the DVB demux via `flexcop_pass_dmx_packets()` and `flexcop_pass_dmx_data()`, FlexCop SRAM and PID filter helpers, Linux workqueues, shared IRQ handling, spinlocks, and the coherent DMA helpers from `flexcop-dma.c`.

## Risks and Edge Cases
The ISR returns `IRQ_NONE` when no DMA status bits are set, which matters because the IRQ is shared. The timer IRQ path drops out if the hardware cursor reports a position beyond the allocated ring. Watchdog recovery resets PID filters while holding the demux lock, so feed-list integrity and lock ordering are important. DMA2 is allocated and routed for CA data but normal stream start only actively transfers DMA1. Cleanup relies on `init_state` to avoid double-free paths after partial probe failure.

## Test Signals
Validate PCI probe/remove, BAR mapping, shared IRQ registration, DMA allocation failure unwinding, transport stream delivery with PID filtering enabled and disabled, timer wraparound data feeding, watchdog PID-filter reset after stalled interrupts, and absence of DMA/IRQ use after remove.
