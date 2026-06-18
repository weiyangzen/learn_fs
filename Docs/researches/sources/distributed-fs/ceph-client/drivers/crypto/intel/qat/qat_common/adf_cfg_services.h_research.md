# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_cfg_services.h

## Purpose
This header defines QAT service enums and parsing/query APIs for `ServicesEnabled` configuration.

## Important APIs, Types, And Functions
Important enums are `enum adf_base_services` (`SVC_ASYM`, `SVC_SYM`, `SVC_DC`, `SVC_DECOMP`), `enum adf_extended_services` (`SVC_DCC`), and `enum adf_composed_services` (`SVC_SYM_ASYM`, `SVC_SYM_DC`, `SVC_ASYM_DC`). It also defines `ADF_ONE_SERVICE`, `ADF_TWO_SERVICES`, `ADF_THREE_SERVICES`, `MAX_NUM_CONCURR_SVC`, and declares service parse/query helpers.

## Control Flow
No executable flow exists. The enum values are used as bit positions by `adf_cfg_services.c` and hardware-data callbacks.

## State And Persistence Behavior
No state exists. The header provides compile-time service identity and limits.

## Dependencies And Integration Points
It includes service string definitions and is consumed by Gen4/Gen6 hardware-data code, config parsing, capability calculation, and ring-to-service checks.

## Risks
Enum ordering is ABI inside the driver because masks use enum values as bit indexes. Changing `MAX_NUM_CONCURR_SVC` affects Gen6 ring-pair assignment assumptions.

## Test Signals
Build coverage plus service parsing, Gen4/Gen6 firmware selection, capability masks, and ring service matching validate this header.
