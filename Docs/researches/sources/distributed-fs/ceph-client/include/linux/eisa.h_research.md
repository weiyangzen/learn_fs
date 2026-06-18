# sources/distributed-fs/ceph-client/include/linux/eisa.h

Purpose: defines the Linux EISA bus/device/driver interface and root-bus registration metadata.

Important APIs/types/functions: slot/resource limits, EISA register offsets, `struct eisa_device`, `struct eisa_driver`, `struct eisa_root_device`, `to_eisa_device()`, `to_eisa_driver()`, `eisa_get_region_index()`, `eisa_driver_register()`, `eisa_driver_unregister()`, driver data helpers, `eisa_root_register()`, and `EISA_bus`.

Control flow: architecture/platform code registers an EISA root with bus base/resources; the bus probes slots, creates `eisa_device` instances, and driver core matches `eisa_driver.id_table`. Without `CONFIG_EISA`, register/unregister helpers compile to no-ops.

State/persistence: hardware slot identity and resources are persistent platform state; kernel state is represented in `struct device`, resource arrays, pretty names, DMA mask, and root bus bookkeeping.

Dependencies/integration: Linux device model, ioport resources, module device tables, and legacy ISA/EISA hardware probing.

Risks/test signals: risks are incorrect I/O offset arithmetic, force-probing absent slot 0, DMA mask inheritance, resource conflicts, and no-op stubs hiding missing support. Test on EISA-capable emulation/hardware or with probe fixtures for slot signatures, resource claiming, driver binding/unbinding, and CONFIG_EISA off builds.
