# sources/distributed-fs/ceph-client/drivers/staging/vme_user/vme_tsi148.c

## Purpose
Implements the real PCI driver for the Tundra/Tempe TSI148 VME-PCI bridge. It maps the chip register block, exposes VME framework resources, programs inbound/outbound translation windows, handles VME/PCI/DMA/location-monitor interrupts, builds DMA linked lists, supports RMW and generated VME IRQs, and configures CR/CSR space.

## Important APIs, Types, and Functions
Important regions are PCI probe/remove (`tsi148_probe()`, `tsi148_remove()`), interrupt setup/dispatch (`tsi148_irq_init()`, `tsi148_irqhandler()`, `tsi148_irq_set()`, `tsi148_irq_generate()`), slave translation (`tsi148_slave_set/get()`), master translation and access (`tsi148_master_set/get/read/write/rmw()`), DMA (`tsi148_dma_list_add/exec/empty()`, VME attribute encoders), location monitors (`tsi148_lm_set/get/attach/detach()`), CR/CSR (`tsi148_crcsr_init/exit()`), and coherent allocation wrappers.

## Control Flow
Probe enables the PCI device, requests BARs, maps BAR0, validates the vendor ID, initializes queues and mutexes, requests IRQs, allocates VME resource objects, fills bridge callbacks, configures CR/CSR space, registers the bridge, and clears board-fail/power-reset state. Resource callbacks translate framework attributes into big-endian TSI148 registers. Master set allocates a PCI memory resource and ioremaps it before programming outbound translation registers. DMA list add allocates a hardware descriptor, fills source/destination/count fields in big-endian format, maps it for DMA, and links descriptors. DMA exec writes the first descriptor address to channel registers, starts `DGO`, waits for IRQ wakeup, and checks `DSTA`.

## State and Persistence Behavior
Persistent runtime state lives in `struct tsi148_driver`: MMIO base, DMA/IACK wait queues, LM callbacks, CR/CSR coherent image, optional flush master image, and mutexes for RMW and generated IRQ serialization. Window configuration persists in chip registers and in allocated PCI resources. DMA descriptors persist in list entries until `tsi148_dma_list_empty()`.

## Dependencies and Integration Points
Depends on PCI, MMIO, DMA mapping, wait queues, IRQs, big-endian register access, and the VME framework. `vme_user` can consume the master/slave/IRQ callbacks. The `err_chk` module parameter integrates VME exception interrupts with generic VME error-handler windows.

## Risks and Test Signals
`tsi148_dma_busy()` returns false-like `0` when busy and true-like `1` when not busy, so its name is misleading but matches wait predicates. Generated IRQ wait lacks a timeout. Some callback paths do not range-check monitor/statid inputs at this layer. Error-check handlers are installed while holding master spinlocks, making interrupt/error-list behavior worth lockdep review. Test signals include PCI probe/remove, window alignment rejection, A16/A24/A32/A64 translations, master read/write with and without `err_chk`, DMA completion/abort/error paths, location monitor interrupts, VME IRQ request/generate/free, and CR/CSR mapping by geographic address.
