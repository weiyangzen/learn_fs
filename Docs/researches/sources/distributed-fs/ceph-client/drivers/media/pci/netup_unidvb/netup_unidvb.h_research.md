# sources/distributed-fs/ceph-client/drivers/media/pci/netup_unidvb/netup_unidvb.h

- Purpose: Shared definitions for the NetUP Universal Dual DVB-CI PCIe driver.
- Important APIs/types/functions: Driver/version/vendor constants, IRQ register offsets and bits, hardware revision enum, `struct netup_dma`, `enum netup_i2c_state`, `struct netup_i2c`, `struct netup_ci_state`, `struct netup_unidvb_dev`, and prototypes for I2C/CI/SPI helpers.
- Control flow: Core code maps MMIO, allocates DMA, registers two frontends, initializes two I2C controllers, CI slots, SPI, and dispatches interrupts to the declared handlers. DMA structs combine ring buffers, work, timeout, and register pointers; I2C state machine uses wait queues and spinlocks.
- State and persistence: Device state includes PCI coordinates, MMIO windows, DMA memory, frontend arrays, workqueue, DMA/I2C/CI/SPI state, and hardware revision. No file persistence in this header.
- Dependencies and integration points: Integrates Linux PCI, I2C, workqueues, videobuf2 DVB, V4L2 device/common, DVB CA EN50221, and companion core/I2C/CI/SPI source files.
- Risks: Shared state is interrupt-heavy: DMA ring, I2C state, CI status, and SPI IRQs need careful locking. Hardware revision constants select different frontend stacks elsewhere.
- Test signals: Compile all companion objects, probe both hardware revisions, exercise DMA IRQs, I2C transfers, CAM interrupts, and SPI initialization/release.
