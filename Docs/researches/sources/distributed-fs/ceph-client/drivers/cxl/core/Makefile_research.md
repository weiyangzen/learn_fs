
# sources/distributed-fs/ceph-client/drivers/cxl/core/Makefile

Purpose: Kbuild rules for the CXL core library/module.

Important APIs, types, and functions: builds `cxl_core.o` under `CONFIG_CXL_BUS` and `suspend.o` under `CONFIG_CXL_SUSPEND`. `cxl_core-y` includes port, pmem, regs, memdev, mbox, pci, hdm, pmu, cdat, optional trace, region, MCE, features, EDAC, RAS, RCH RAS, and ATL objects. `ccflags-y` adds the parent CXL include path and trace include settings.

Control flow: no runtime logic. Object composition determines which core services and exported symbols are available.

State and persistence: no runtime state.

Dependencies and integration points: integrates with the top-level CXL Makefile and Kconfig feature gates. `cdat.o` is always part of core when CXL_BUS is enabled; `atl.o` is conditional on `CONFIG_CXL_ATL`.

Risks and test signals: optional object combinations must match declarations/stubs in `core.h`. Trace include path flags are sensitive to build location. Test signals are build coverage across CONFIG_CXL_REGION/RAS/FEATURES/ATL permutations and module namespace export checks.
