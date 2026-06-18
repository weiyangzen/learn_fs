<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_aca.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_aca.h

## Purpose
`amdgpu_aca.h` defines the internal Accelerator Check Architecture interface for amdgpu RAS. It provides register bitfield decoders, ACA register indices, hardware IP and error-type enums, bank and handle data structures, SMU callback contracts, and public functions used by RAS blocks to register ACA handles and query error data.

## Important APIs, types, and functions
- Register helpers such as `ACA_REG__STATUS__UC()`, `ADDRV()`, `CECC()`, `UECC()`, `DEFERRED()`, `POISON()`, `ERRORCODEEXT()`, `ACA_REG__IPID__HARDWAREID()`, and `ACA_REG__MISC0__ERRCNT()` decode 64-bit bank registers.
- `enum aca_reg_idx` defines the 16-slot register dump layout, including control, status, address, misc, config, IPID, syndrome, deferred status/address, and control mask.
- `enum aca_hwip_type`, `enum aca_error_type`, and `enum aca_smu_type` define dispatch and accounting domains.
- `struct aca_bank` stores a bank's SMU error type, parsed ACA error type, and raw register array.
- `struct aca_handle` represents one registered RAS block's ACA binding, including device, manager, error cache, bank operations, sysfs attribute, name, mask, and private data.
- `struct aca_bank_ops` lets a handle validate and parse banks.
- `struct aca_smu_funcs` is the platform callback table for SMU debug mode, valid-bank count, valid-bank fetch, and error-code parsing.
- `struct amdgpu_aca` is embedded in `struct amdgpu_device`.
- Public functions include lifecycle, SMU-function installation, handle registration/removal, error-data query, bank-info decode, error-code check, debug mode/debugfs helpers, and direct cache logging.

## Control flow
This header has no executable flow, but it defines the flow used by `amdgpu_aca.c`: platform code installs `aca_smu_funcs`; RAS blocks add `aca_handle` objects with `aca_info` and `aca_bank_ops`; query code fetches banks through SMU callbacks; banks are filtered/parsed by handle callbacks; parsed counts are accumulated into handle error caches and later drained into RAS data.

## State and persistence behavior
The data structures describe transient kernel state. `aca_handle_manager` tracks live handles, `aca_error_cache` stores accumulated per-handle counts, and `amdgpu_aca` stores the SMU callback table and UE update flag. The header defines no persistent storage or firmware ABI beyond numeric bit definitions matching ACA register formats.

## Dependencies and integration points
The header depends on Linux lists and forward-declared RAS query/counting types. It is included by `amdgpu.h`, `amdgpu_aca.c`, and RAS hardware blocks that need to register ACA handlers or use bank decode helpers. It also encodes SMN base constants for SMU MCA banks.

## Risks and edge cases
Bitfield macros are register-format contracts. Incorrect high/low bit positions would misclassify error validity, UE/CE/deferred/poison status, address validity, or bank identity. The enum ordering of `aca_error_type` is used with `BIT_MASK()` masks, so reordering values affects handle masks.

The misspelled `ACA_HWIP_TYPE_UNKNOW` and `ACA_BANK_ERR_IS_DEFFERED` are part of the current internal API spelling and should not be renamed casually. `ACA_MAX_REGS_COUNT` must stay consistent with `ACA_REG_IDX_COUNT` and all register dump indices.

## Test signals
Compile-time coverage should include all RAS blocks that include this header. Runtime signals are correct bank register dumps, correct `aca_bank_info_decode()` output for known IPID values, correct masks for UE/CE/deferred queries, and successful SMU callback integration on ACA-enabled ASICs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_aca.h -->
