# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/pmc/ssram_telemetry.h

Purpose: declares the minimal SSRAM telemetry data contract between the SSRAM PCI driver and the PMC core driver.

Important APIs/types/functions: `struct pmc_ssram_telemetry` carries a PMC device ID and PWRM base address. `pmc_ssram_telemetry_get_pmc_info()` retrieves one indexed PMC's cached information.

Control flow: `core.c` calls the declared function from `pmc_core_pmc_add()` during SSRAM-backed generic init. The implementation may return success, `-EAGAIN`, `-EINVAL`, or `-ENODEV`.

State and persistence: no header state. The structure is a copy-out container for implementation-owned state in `ssram_telemetry.c`.

Dependencies and integration points: included by `core.c` and `ssram_telemetry.c`; depends on core definitions for `MAX_NUM_PMC` and indexes indirectly through callers.

Risks: the API only exposes `devid` and `base_addr`, so any future need for per-PMC metadata requires extending this interface. Callers must understand `-EAGAIN` as probe ordering, not permanent absence.

Test signals: compile coverage for both implementation and consumer; runtime SSRAM init should correctly map returned `devid` through the platform `pmc_info` list.
