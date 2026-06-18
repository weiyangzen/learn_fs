# sources/distributed-fs/ceph-client/drivers/misc/ocxl/config.c

## Purpose
This file parses and programs OpenCAPI/OCXL PCI configuration space, especially DVSEC capabilities for functions, AFUs, transaction layer, ACTAGs, PASIDs, MMIO templates, LPC memory, reset/reload, and PASID termination.

## Important APIs, types, and functions
Public functions include `ocxl_config_read_function()`, `ocxl_config_check_afu_index()`, `ocxl_config_read_afu()`, `ocxl_config_get_reset_reload()`, `ocxl_config_set_reset_reload()`, `ocxl_config_get_actag_info()`, `ocxl_config_set_afu_actag()`, `ocxl_config_get_pasid_info()`, `ocxl_config_set_afu_pasid()`, `ocxl_config_set_afu_state()`, `ocxl_config_set_TL()`, `ocxl_config_terminate_pasid()`, and `ocxl_config_set_actag()`. Internal readers parse PASID capability, TL/function/AFU/vendor DVSECs, AFU names, template versions, MMIO, control, and memory sizes.

## Control flow and state
Function read locates required DVSECs, validates AFU/PASID consistency, logs vendor info, and records offsets. AFU read selects an AFU index in the AFU-info DVSEC, reads template fields with a valid-bit polling loop, validates names and BARs, locates AFU-control DVSEC, and extracts supported ACTAG/PASID values. Programming helpers set ACTAG/PASID bases, enable/disable AFUs, configure TL transmit/receive capabilities with platform firmware calls, and terminate PASIDs with a busy-bit timeout.

## State and persistence behavior
This code writes PCI config registers and platform TL state; changes persist in device runtime configuration until reset or driver teardown. Parsed configuration is stored in `ocxl_fn_config` and `ocxl_afu_config` held by core structures.

## Dependencies and integration points
It depends on PCI extended capabilities, OCXL config constants, PowerNV platform functions (`pnv_ocxl_*`), and internal OCXL structures. `core.c` uses it during function/AFU initialization and context detach.

## Risks and test signals
Risks include DVSEC offset assumptions, valid-bit polling timeouts, template version/length compatibility, unaligned/name parsing, total-memory shifts with large sizes, TL rate endianness, PASID termination timeout leaving unsafe state, and vendor function-0 reference handling. Test signals include devices with holes in AFU index map, missing malformed DVSECs, AFU name validation, TL setup, ACTAG/PASID programming, PASID terminate success/timeout, and reset/reload access on nonzero functions.
