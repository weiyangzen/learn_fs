# sources/distributed-fs/ceph-client/drivers/acpi/apei/einj-cxl.c

## Purpose
Provides CXL-facing wrappers around EINJ so CXL core can list and inject CXL cache/memory protocol errors through ACPI firmware.

## Important APIs, Types, And Functions
Exports `einj_cxl_available_error_type_show()`, `einj_cxl_inject_rch_error()`, `einj_cxl_inject_error()`, and `einj_cxl_is_initialized()` in the `CXL` namespace. `cxl_dport_get_sbdf()` converts a downstream port PCI device to the segment:bus:device:function encoding required by ACPI EINJ.

## Control Flow
The show helper queries EINJ available types and prints only CXL masks. RCH injection validates the type and calls `einj_cxl_rch_error_inject()` with memory-address flags and the RCRB base. Non-RCH injection validates the type, derives SBDF from the PCI host bridge and device function, then calls `einj_error_inject()` with the PCIe SBDF flag.

## State And Persistence
This file holds only a static string table. Initialization state comes from `einj_initialized` in `einj-core.c`.

## Dependencies And Integration Points
Integrates CXL core with APEI EINJ exports, PCI host bridge/domain numbering, `seq_file`, and `cxl/einj.h`.

## Risks
Incorrect SBDF encoding or missing host bridge information rejects injection. The CXL RCH path passes an MMIO RCRB base through a special EINJ path, so validation must remain coupled to CXL-specific callers.

## Test Signals
Check CXL debugfs/sysfs consumers for listed CXL types, invalid non-CXL type rejection, host bridge domain handling, RCH RCRB injection call parameters, and namespace symbol resolution.
