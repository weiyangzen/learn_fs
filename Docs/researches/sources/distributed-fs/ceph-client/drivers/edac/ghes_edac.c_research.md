# sources/distributed-fs/ceph-client/drivers/edac/ghes_edac.c

## Purpose
This driver bridges ACPI APEI/GHES firmware memory-error reports into the EDAC memory-controller reporting path. It builds a logical EDAC memory controller from SMBIOS/DMI DIMM data and reports CPER memory error sections through EDAC raw error handling.

## Important APIs and Functions
`assign_dmi_dimm_info()` converts SMBIOS Type 17 fields into EDAC DIMM size/type/mode/label data. `ghes_scan_system()` walks DMI once. `ghes_edac_report_mem_error()` is the notifier callback that translates CPER severity, address, grain, error type, location, and module handle into `edac_raw_error_desc`. `ghes_edac_register()` and `ghes_edac_unregister()` manage a singleton EDAC controller with reference counting across GHES devices.

## Control Flow
Module init obtains the GHES device list and registers each device. The first registration scans DMI, allocates a single all-memory EDAC controller, fills DIMM metadata or a fake fallback DIMM, adds it to EDAC, publishes `ghes_pvt` under a spinlock, and registers the GHES report notifier. Subsequent registrations only increment `ghes_refcount`. Error reports take `ghes_lock`, copy the singleton private pointer, clear shared buffers, fill the raw EDAC descriptor from CPER fields, and call `edac_raw_mc_handle_error()`. Unregister decrements the refcount, nulls `ghes_pvt`, removes the EDAC controller, and unregisters the notifier.

## State and Persistence
State includes `ghes_refcount`, `ghes_pvt`, `ghes_hw` DMI DIMM cache, `system_scanned`, `ghes_devs`, a registration mutex, and a spinlock protecting report-time buffers. State is runtime only and rebuilt on module load.

## Dependencies and Integration
The driver depends on ACPI GHES APIs, DMI helpers, CPER/RAS helpers, notifier chains, EDAC core allocation/reporting, and `edac_module.h`.

## Risks
Firmware data quality is central; missing SMBIOS DIMMs triggers a fake DIMM and explicit caution logs. Report buffers are shared through the singleton private object and require `ghes_lock`. The callback warns if called from NMI because it assumes GHES deferred processing.

## Test Signals
Signals include EDAC controller registration on systems with GHES devices, DMI-derived DIMM labels and SMBIOS handles, CPER corrected/recoverable/panic severity mapping, correct PFN/offset/grain fields, and clean behavior when DMI has no DIMMs.
