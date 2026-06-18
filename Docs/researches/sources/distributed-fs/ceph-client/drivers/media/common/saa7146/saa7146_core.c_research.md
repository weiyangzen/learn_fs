# sources/distributed-fs/ceph-client/drivers/media/common/saa7146/saa7146_core.c

Purpose: base PCI driver framework for SAA7146 devices: extension registration, PCI probe/remove, IRQ dispatch, GPIO/DEBI helpers, and DMA page-table allocation/building.

Important APIs/functions: exports `saa7146_register_extension()`, `saa7146_unregister_extension()`, `saa7146_setgpio()`, DEBI wait helper, page-table helpers, vmalloc-backed page-table helpers, `saa7146_i2c_adapter_prepare`, and debug state. Internal `saa7146_init_one()` performs PCI enable, BAR mapping, IRQ registration, coherent RPS/I2C memory allocation, extension probe/attach, and drvdata setup.

Control flow: the shared interrupt handler acknowledges ISR bits, delegates extension IRQs, routes RPS0/RPS1 to VV callbacks, wakes I2C waiters, disables unhandled sources, then writes ISR ack. Remove calls extension detach, stops DMA/IRQs, frees coherent blocks, unmaps BAR, disables PCI, and frees `dev`.

State/persistence: runtime state is `struct saa7146_dev`, coherent RPS/I2C buffers, locks, wait queues, IRQ masks, and global device count/debug parameter. No durable persistence.

Dependencies/integration: extension modules supply PCI IDs, probe/attach/detach/IRQ callbacks. Base relies on Linux PCI, DMA, IRQ, I2C, V4L2 device embedding, and SAA7146 register macros.

Risks/test signals: partial-probe unwind, shared IRQ masking, I2C IRQ races, DMA mapping failures, and extension callback errors are key. Test by injecting failures at each allocation/register stage, exercising extension IRQ masks, and validating remove after failed/partial attach.
