# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_core.h

- Purpose: Central MGB4 constants, module-type predicates, DMA channel descriptor, and device state structure.
- Important APIs/types/functions: `MGB4_HW_FREQ`, device counts, `MGB4_IS_*` and `MGB4_HAS_VOUT` macros, `struct mgb4_dma_channel`, and `struct mgb4_dev`.
- Control flow: All MGB4 modules include this to share the detected module type, register mappings, child devices, V4L2 endpoint pointers, DMA channels, flash metadata, trigger, hwmon, and reconfiguration bit.
- State and persistence: `struct mgb4_dev` owns volatile kernel resources and names for persistent flash partitions; `io_reconfig` serializes cross-endpoint source changes.
- Dependencies and integration points: Couples core, DMA, I2C, regs, vin/vout, sysfs, trigger, SPI/MTD, clock, and hwmon code.
- Risks: Module-type macros encode hardware policy in bit shifts; future module versions need updates. Shared pointers require careful remove ordering.
- Test signals: Compile coverage plus probe tests for FPDL3, GMSL1, GMSL3, GMSL3C, and no-module cases.
