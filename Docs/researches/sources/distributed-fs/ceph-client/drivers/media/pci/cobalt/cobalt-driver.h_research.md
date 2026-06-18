<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-driver.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-driver.h

Purpose: Defines the Cobalt driver's core constants, register layout, logging macros, DMA/helper structs, per-stream state, per-card state, and MMIO/bus accessors.

Important APIs/types: `struct cobalt_stream` models one video/audio input/output or dummy stream, including `video_device`, `vb2_queue`, buffer list, subdevice, locks, DV timings, format fields, DMA channel, IRQ masks, descriptor info, stability flags, role flags, parent pointer, and ALSA pointer. `struct cobalt` owns card-wide PCI/V4L2/MMIO/I2C/IRQ/DMA/flash state. Helper types include `cobalt_i2c_data`, `pci_consistent_buffer`, `sg_dma_desc_info`, and `cobalt_buffer`. Inline helpers read/write BAR0/BAR1, sysctrl/sysstat, and Cobalt bus windows.

Control flow: No standalone flow, but the macros and structs drive all Cobalt modules. Stream fields are initialized in `cobalt-driver.c`, consumed by V4L2/vb2/IRQ/ALSA/DMA code, and torn down during node and PCI removal.

State/persistence: This header defines the in-memory state graph for the driver. Persistent hardware state is accessed through sysctrl/sysstat and bus macros. `cobalt_s_bit_sysctrl()` serializes read-modify-write with `pci_lock`.

Dependencies/integration: Includes V4L2/vb2 DMA-SG, PCI, I2C, workqueue, mutex/spinlock, and generated FPGA register-map headers. It is the common dependency for all Cobalt implementation files.

Risks: Many hardware addresses and bit masks are hard-coded. `COBALT_NUM_STREAMS` differs from `DMA_CHANNELS_MAX`, so loops must use the right bound. `cobalt_bus_write32()` takes a `u16 data` parameter despite writing 32 bits, which is surprising and can truncate callers that expect full 32-bit writes. Inline bus macros depend on local variable naming in macro definitions.

Test signals: Build coverage across all Cobalt objects, static analysis for struct/loop bounds, sysctrl concurrent updates, DMA descriptor allocation for all stream types, and register access on real hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/cobalt/cobalt-driver.h -->
