
# sources/distributed-fs/ceph-client/drivers/cxl/Kconfig

Purpose: top-level configuration menu for Compute Express Link support, including bus core, PCI/memory devices, ACPI platform discovery, persistent memory, regions, RAS, ATL, and optional EDAC/features.

Important APIs, types, and functions: `menuconfig CXL_BUS` enables the subsystem and selects firmware/PCI DOE support. Key options are `CXL_PCI`, `CXL_MEM_RAW_COMMANDS`, `CXL_ACPI`, `CXL_PMEM`, `CXL_MEM`, `CXL_FEATURES`, EDAC feature toggles, internal `CXL_PORT`, `CXL_SUSPEND`, `CXL_REGION`, `CXL_REGION_INVALIDATION_TEST`, `CXL_MCE`, `CXL_RAS`, and `CXL_ATL`.

Control flow: Kconfig dependencies determine which CXL source files compile and which stubs in headers are active. `CXL_ACPI` defaults to `CXL_BUS` and selects `CXL_PORT`; `CXL_REGION` defaults to enabled with sparsemem; `CXL_ATL` is enabled only with region support, ACPI PRMT, and AMD_NB.

State and persistence: no runtime state. It controls kernel configuration state and available module/built-in features.

Dependencies and integration points: integrates with PCI, ACPI, LIBNVDIMM, sparsemem, FWCTL, EDAC, tracing/RAS, x86 MCE, and platform firmware features. These options gate the Makefile and `core.h` APIs used by ACPI/CDAT/ATL files.

Risks and test signals: configuration combinations are the risk, especially built-in ordering, optional region/RAS/features stubs, and EDAC dependencies. Test signals include allyesconfig/allmodconfig, CXL_BUS without CXL_REGION, CXL_ACPI as module, CXL_ATL dependency satisfaction, and production kernels keeping `CXL_REGION_INVALIDATION_TEST` disabled.
