# sources/distributed-fs/ceph-client/include/cxl/cxl.h

Purpose: defines core CXL device-state, register-map, DPA partition, and device-state allocation contracts shared by CXL memory and Type-2 drivers.

Important APIs, types, and flow: `enum cxl_devtype` distinguishes vendor-specific Type-2 device memory from class memory Type-3 devices. `struct cxl_regs` groups mapped component, device, PMU, RCH, and RCD register block pointers. Register-map structs describe DVSEC-harvested offsets/sizes and the active register type. `struct cxl_dpa_perf` and `cxl_dpa_partition` model DPA resources, QoS/access coordinates, and RAM/PMEM mode. `struct cxl_dev_state` owns the device pointer, memdev, register maps, parsed device registers, DVSEC offset, RCD/media readiness flags, DPA resource tree, partitions, serial/type, mailbox, and optional features state. `devm_cxl_dev_state_create()` enforces that driver-specific structs embed `cxl_dev_state` at offset zero and delegates to `_devm_cxl_dev_state_create()`.

State and persistence: runtime state is devm-managed per CXL device. DPA resources and partitions model device capacity during the driver lifetime; no direct persistence is handled here.

Dependencies and integration: depends on Linux resources, NUMA/access coordinates, CXL mailbox/features, memdev objects, PCI DVSEC discovery, and register mapping code.

Risks and test signals: risks include wrong register-block offsets, Type-2 embedding contract violations, DPA partition/resource overlap, and optional feature-state Kconfig assumptions. Signals include CXL probe tests, DVSEC/register-map validation, Type-2 driver compile/runtime tests, DPA partition creation tests, and mailbox/no-mailbox device coverage.
