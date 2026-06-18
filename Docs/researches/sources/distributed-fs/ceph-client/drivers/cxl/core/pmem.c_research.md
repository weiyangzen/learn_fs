# sources/distributed-fs/ceph-client/drivers/cxl/core/pmem.c

Purpose: implements CXL persistent-memory bridge devices that connect the CXL topology to the LIBNVDIMM subsystem. It creates root-level `cxl_nvdimm_bridge` devices for persistent-memory capable CXL roots and per-memdev `cxl_nvdimm` devices that host LIBNVDIMM dimm objects.

Important APIs, types, and functions: exported APIs are `to_cxl_nvdimm_bridge()`, `cxl_find_nvdimm_bridge()`, `__devm_cxl_add_nvdimm_bridge()`, `is_cxl_nvdimm()`, `to_cxl_nvdimm()`, and `devm_cxl_add_nvdimm()`. Device types are `cxl_nvdimm_bridge_type` and `cxl_nvdimm_type`. Allocation helpers are `cxl_nvdimm_bridge_alloc()` and `cxl_nvdimm_alloc()`, with cleanup through `unregister_nvb()` and `cxlmd_release_nvdimm()`.

Control flow: bridge creation is skipped when `CONFIG_CXL_PMEM` is disabled, otherwise it allocates an IDA ID, initializes a CXL bus device below the root port, adds it, verifies that a driver attached, and registers devm cleanup. `cxl_find_nvdimm_bridge()` walks from any descendant port to the root and finds a child with bridge device type. Per-memdev addition locates the bridge, locks the root uport and bridge device to ensure `nvdimm_bus` is registered, allocates a `cxl_nvdimm`, names it `pmem%d`, adds it, and registers cleanup.

State and persistence behavior: bridge IDs are IDA-managed until release. `cxl_nvdimm_bridge` stores its root port and `nvdimm_bus` pointer as bridge-driver state. `cxl_nvdimm` stores a backpointer to `cxlmd`, and `cxlmd` stores `cxl_nvd` and `cxl_nvb` while the bridge is active. The NVDIMM device ID string is derived from the CXL serial and persists for device lifetime, not across hardware identity changes.

Dependencies and integration points: depends on CXL bus type and base attributes, root lookup via `find_cxl_root()`, memdev objects from `memdev.c`, and the external `cxl_pmem`/LIBNVDIMM driver that binds bridge and dimm devices. It provides the object layer used by label-storage and namespace operations outside this file.

Risks: bridge creation intentionally fails if no bridge driver attaches; ordering with `cxl_acpi_probe()` is protected by locks in `devm_cxl_add_nvdimm()`. Reference handling is delicate because memdevs hold a bridge reference until `cxlmd_release_nvdimm()`. Error paths must clear `cxlmd->cxl_nvb` and `cxlmd->cxl_nvd` to avoid dangling links.

Test signals: build with `CONFIG_CXL_PMEM` enabled and disabled, root bridge driver attach failure, finding a bridge from nested ports, per-memdev add before and after `nvdimm_bus` registration, add failure after name/device_add, teardown ordering of memdev and bridge, and stable dimm ID based on serial.
