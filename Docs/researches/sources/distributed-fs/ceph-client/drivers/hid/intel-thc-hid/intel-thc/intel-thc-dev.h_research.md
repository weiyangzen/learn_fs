# sources/distributed-fs/ceph-client/drivers/hid/intel-thc-hid/intel-thc/intel-thc-dev.h

Purpose: public interface and central device state for Intel THC common helpers. It defines port types, interrupt bit positions, `struct thc_device`, and prototypes exported by `intel-thc-dev.c`.

Important APIs/types: `enum thc_port_type` selects SPI or I2C operation. `enum thc_int_type` maps returned interrupt flags. `struct thc_device` owns regmap/MMIO pointers, bus mutex, DMA context, wake-on-touch data, write/SWDMA waitqueues, performance throttling, I2C sub-IP register shadow, and I2C feature flags.

Control flow: protocol drivers include this header, allocate the context through `thc_dev_init()`, select/configure a port, configure interrupts/DMA, perform PIO/DMA I/O, and use save/restore helpers for power-management paths.

State and persistence: the header makes explicit which state survives across helper calls: DMA context, WOT state, `i2c_subip_regs`, and enable flags used to restore features temporarily disabled during SWDMA.

Dependencies and integration: includes DMA and WOT headers and Linux locking/workqueue headers. It is the shared ABI between Intel THC common code and transport-specific QuickSPI/QuickI2C drivers.

Risks: exported prototypes expose low-level hardware operations without type-level sequencing guarantees, so callers must configure port type, max packet sizes, DMA allocation, and interrupt mode in the correct order.

Test signals: compile coverage for all prototypes, namespace export resolution, and integration tests that instantiate both SPI and I2C ports.
