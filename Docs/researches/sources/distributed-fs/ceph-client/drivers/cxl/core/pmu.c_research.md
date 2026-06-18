# sources/distributed-fs/ceph-client/drivers/cxl/core/pmu.c

Purpose: creates CXL PMU bus devices from discovered PMU register blocks. It is small device-model glue that publishes a PMU child device with association ID, index, type, and register base for a PMU driver to bind.

Important APIs, types, and functions: exported API is `devm_cxl_pmu_add()`. The device type is `cxl_pmu_type`, with release callback `cxl_pmu_release()`. `remove_dev()` unregisters the device through devm cleanup. The allocated object is `struct cxl_pmu`, populated from `struct cxl_pmu_regs`, association ID, index, and `enum cxl_pmu_type`.

Control flow: `devm_cxl_pmu_add()` allocates a zeroed PMU object, copies identifying fields and `regs->pmu` base, initializes a CXL bus device below the parent, marks PM not required, names memdev PMUs as `pmu_mem%d.%d`, adds the device, then registers a devm action to unregister it with the parent. Errors before `device_add()` drop the device reference.

State and persistence behavior: PMU state lives in the child device for its lifetime. The register base is an MMIO pointer discovered elsewhere and only stored here. There is no filesystem persistence or runtime counter management in this file; actual PMU operation belongs to the binding driver.

Dependencies and integration points: depends on CXL bus type, CXL PMU type definitions from `<pmu.h>`/`<cxlmem.h>`, and register discovery code that supplies `struct cxl_pmu_regs`. The device name and type are the handoff contract to the PMU driver.

Risks: the switch currently handles `CXL_PMU_MEMDEV`; adding new PMU types without a naming case would leave `rc` undefined or fail unpredictably. The file assumes the parent owns the register mapping lifetime for `pmu->base`. Because cleanup is devm-attached to the parent, parent teardown must outlive any PMU driver access.

Test signals: create memdev PMUs with multiple association IDs and indices, verify device names and CXL bus type, bind/unbind the PMU driver, parent teardown unregisters children, allocation/name/device_add failure paths release memory, and compile coverage when adding new `enum cxl_pmu_type` values.
