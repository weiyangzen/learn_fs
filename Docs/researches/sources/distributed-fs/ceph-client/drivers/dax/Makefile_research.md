# sources/distributed-fs/ceph-client/drivers/dax/Makefile

Purpose: build recipe for DAX core and DAX consumer/provider modules.

Important APIs/types/functions: builds `dax.o` from `super.o` and `bus.o`, `device_dax.o` from `device.o`, `dax_pmem.o`, `dax_cxl.o`, `fsdev_dax.o`, and always descends into `hmem/`.

Control flow and state: object inclusion follows Kconfig symbols. DAX core is built when `CONFIG_DAX` is enabled; specific consumers are separate modules/objects keyed by `CONFIG_DEV_DAX*`.

Dependencies and integration: integrates with kernel kbuild and DAX Kconfig, ensuring core bus/super objects are available before device drivers that register on that bus.

Risks and test signals: missing object linkage causes unresolved symbols such as DAX bus registration or exported constructors. Test module builds for each Kconfig combination, especially FSDEV and CXL/PMEM split modules.
