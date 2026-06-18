# sources/distributed-fs/ceph-client/drivers/acpi/apei/ghes_helpers.c

## Purpose
Provides CXL CPER protocol-error helper routines used by GHES and CXL workqueue consumers.

## Important APIs, Types, And Functions
Exports `cxl_cper_sec_prot_err_valid()` and `cxl_cper_setup_prot_err_work_data()`. These operate on `struct cxl_cper_sec_prot_err` and fill `struct cxl_cper_prot_err_work_data`.

## Control Flow
Validation requires agent address and protocol error log valid bits, a RAS capability size matching `struct cxl_ras_capability_regs`, and warns if device-like agents lack serial number. Setup accepts known CXL agent types, copies the CPER protocol section, skips DVSEC bytes, copies the RAS capability registers, and maps CPER severity to AER severity.

## State And Persistence
No file-local state. Output state is the work-data object passed by caller.

## Dependencies And Integration Points
Depends on CXL event structures, AER severity conversion, and GHES CXL protocol error dispatch.

## Risks
The helper assumes the caller has already ensured enough backing CPER section data for the DVSEC and RAS capability offsets. Invalid agent types and unexpected RAS sizes are rejected.

## Test Signals
Cover missing valid bits, bad `err_len`, missing serial warning cases, each accepted agent type, rejected default agent type, and severity conversion.
