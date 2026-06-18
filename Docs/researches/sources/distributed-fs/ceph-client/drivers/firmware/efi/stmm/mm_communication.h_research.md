# sources/distributed-fs/ceph-client/drivers/firmware/efi/stmm/mm_communication.h

Purpose: Defines the wire-format contract between Linux EFI variable code and StandaloneMM (StMM) running inside OP-TEE. It is a protocol header, not executable code, and keeps Linux-side struct layouts aligned with EDK2/PI concepts such as EFI_MM_COMMUNICATE_HEADER and SMM variable command payloads.

Important APIs/types/functions: The main types are `efi_mm_communicate_header`, `smm_variable_communicate_header`, `smm_variable_access`, `smm_variable_payload_size`, `smm_variable_getnext`, `smm_variable_query_info`, `var_check_property`, and `smm_variable_var_check_property`. Constants identify the OP-TEE pseudo-TA (`PTA_STMM_UUID`), the EFI MM variable GUID, the PTA command (`PTA_STMM_CMD_COMMUNICATE`), SPM return codes, and StMM variable function IDs for get/set/query/enumerate/property/payload calls.

Control flow: No runtime flow is implemented here. Consumers allocate a communication buffer beginning with `efi_mm_communicate_header`, place a `smm_variable_communicate_header` in `data`, then append the function-specific payload type described by the `SMM_VARIABLE_FUNCTION_*` selector.

State and persistence behavior: The header describes persistent EFI variables and variable property metadata but stores no state itself. Fields such as name/data sizes and variable attributes are passed through to secure firmware, where persistent storage decisions are made.

Dependencies and integration points: Depends on kernel EFI GUID/status types, `BIT()`, and packed/flexible-array conventions. It is directly included by `tee_stmm_efi.c`, which relies on exact field sizes for shared-memory communication with OP-TEE and StandaloneMM.

Risks and test signals: Layout drift, size_t width assumptions, or GUID endian confusion would break the secure-firmware ABI. Useful tests are compile coverage across supported architectures, EFI variable get/set/enumeration tests through the TEE backend, and negative tests for oversized payloads and read-only property handling.
