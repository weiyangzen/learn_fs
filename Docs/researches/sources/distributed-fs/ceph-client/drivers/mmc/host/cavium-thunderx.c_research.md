# sources/distributed-fs/ceph-client/drivers/mmc/host/cavium-thunderx.c

## Purpose
`cavium-thunderx.c` is the PCI front end for the shared Cavium MMC/eMMC core. It supports ThunderX controllers exposed as Cavium PCI device `0xa010`, maps PCI BARs, enables clocks, configures MSI-X interrupts, creates OF slot child devices, and delegates slot-level behavior to `cavium.c`.

## Important APIs, Types, and Functions
Important functions are `thunder_mmc_acquire_bus`, `thunder_mmc_release_bus`, `thunder_mmc_int_enable`, `thunder_mmc_register_interrupts`, `thunder_mmc_probe`, and `thunder_mmc_remove`. They populate `struct cvm_mmc_host` fields such as `base`, `dma_base`, `reg_off`, `reg_off_dma`, `clk`, `sys_freq`, `use_sg`, `big_dma_addr`, `need_irq_handler_lock`, callbacks, slot arrays, and serializer state.

## Control Flow and State
Probe allocates the common host, enables the PCI device with managed PCI helpers, requests BARs, maps BAR0, uses the same base for DMA registers, sets ThunderX-specific register offsets, enables the controller clock, initializes locking, sets DMA mask to 48 bits, clears stale command/DMA interrupts and DMA FIFO state, allocates one to nine MSI-X vectors, and registers each vector against `cvm_mmc_interrupt` with a descriptive shared IRQ-name table. It then iterates OF children compatible with `mmc-slot`, creates a platform child device for each, and calls `cvm_mmc_of_slot_probe`.

Removal tears down all slot MMC hosts, disables DMA, and disables the clock. Error unwind destroys partially created slot devices and disables the clock.

## State and Persistence Behavior
The file stores no durable state. Runtime state is the PCI driver data pointer to `cvm_mmc_host`, the mapped register window, clock enable state, slot platform devices, and the common host’s active request/slot state. Interrupt enable writes are done through `MIO_EMM_INT` and `MIO_EMM_INT_EN_SET`, while stale DMA IRQ state is cleared during probe.

## Dependencies and Integration Points
Dependencies include PCI managed resource APIs, MSI-X allocation, Linux clk, OF child nodes under a PCI device, DMA masks, and the shared Cavium MMC core exported by `cavium.h`. The file registers `module_pci_driver(thunder_mmc_driver)` and depends on the common `cvm_mmc_interrupt`, `cvm_mmc_of_slot_probe`, and `cvm_mmc_of_slot_remove` entry points.

## Risks and Test Signals
Risks include partial MSI-X vector allocation, OF child lifetime handling, clock cleanup on every error path, lack of explicit `pci_free_irq_vectors` in remove/error paths, and shared-core assumptions about ThunderX register offsets. Test signals include PCI probe/remove, MSI-X vector count from 1 to 9, slot child creation, DMA and command IRQ delivery, clock enable/disable, SG DMA requests, and error unwind with partially initialized slots.
