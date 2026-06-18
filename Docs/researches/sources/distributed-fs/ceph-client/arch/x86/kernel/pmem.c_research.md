# sources/distributed-fs/ceph-client/arch/x86/kernel/pmem.c

## Purpose
Registers an `e820_pmem` platform device when the x86 I/O memory resource tree contains legacy persistent-memory ranges, triggering the NVDIMM e820 driver to load.

## APIs, Types, And Functions
The file defines `found()` as a resource-walk callback and `register_e820_pmem()` as a `device_initcall()`.

## Control Flow
At device init, `register_e820_pmem()` calls `walk_iomem_res_desc()` for `IORES_DESC_PERSISTENT_MEMORY_LEGACY`. If no matching memory resource exists, it exits successfully without registering anything. If found, it allocates a platform device named `e820_pmem` and adds it; failed add releases the device.

## State And Persistence
Persistent state is only the platform device registered with the driver core. The actual persistent-memory resource ownership and NVDIMM behavior live elsewhere.

## Dependencies And Integration
Depends on the iomem resource tree built from E820 data and `drivers/nvdimm/e820.c` for the implementation that binds to the platform device.

## Risks And Test Signals
Risk is mainly missed or duplicate device registration if E820 resource descriptors are wrong. Test signals include the presence of `e820_pmem`, successful nvdimm/e820 driver binding, and namespace discovery on platforms exposing legacy persistent memory.
