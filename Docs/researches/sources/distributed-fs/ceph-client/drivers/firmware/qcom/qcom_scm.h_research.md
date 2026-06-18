# sources/distributed-fs/ceph-client/drivers/firmware/qcom/qcom_scm.h

## Purpose
This private header defines SCM internal call descriptors, argument metadata, transport prototypes, service/command IDs, common SCM error codes, and the shared error remapping helper used by `qcom_scm.c`, `qcom_scm-smc.c`, and `qcom_scm-legacy.c`.

## Important APIs, Types, And Macros
- `enum qcom_scm_convention`: unknown, legacy, ARM32 SMCCC, ARM64 SMCCC.
- `enum qcom_scm_arg_types`: value, read-only buffer, read-write buffer, and buffer-value.
- `QCOM_SCM_ARGS()` encodes argument count and per-argument type tags into the `arginfo` word.
- `struct qcom_scm_desc` carries service, command, argument metadata, up to ten 64-bit args, and owner.
- `struct qcom_scm_res` carries up to three return values.
- Transport prototypes: `__scm_smc_call()`, `scm_legacy_call()`, `scm_legacy_call_atomic()`, and the `scm_smc_call()` wrapper using global convention.
- Service constants cover boot, PIL/PAS, IO, info, memory protection, OCMEM, enterprise security/ICE, HDCP, LMH, SMMU, waitqueue, GPU, and trusted OS SMC invoke.
- `qcom_scm_remap_error()` maps SCM negative status codes to Linux errno.

## Control Flow And Integration
Callers fill `qcom_scm_desc` with IDs and `QCOM_SCM_ARGS()` metadata, then transport files encode it for either modern SMCCC or legacy SMC. `qcom_scm.c` uses these constants to implement higher-level exported APIs. Waitqueue prototypes bridge the SMCCC transport back to the core SCM interrupt/completion handling.

## State And Persistence
The header declares the global `qcom_scm_convention` but owns no storage itself. Its constants define firmware state transitions performed by implementation files.

## Dependencies And Integration Points
It depends on forward declarations for `struct device` and `struct qcom_tzmem_pool`, plus public Qualcomm firmware headers for external types. It is the internal ABI between SCM implementation units.

## Risks
Incorrect `arginfo` encoding or service/command IDs can route secure calls incorrectly. `qcom_scm_remap_error()` defaults unknown errors to `-EINVAL`, which can hide firmware-specific status. The header allows up to ten arguments and three returns; call sites must respect transport-specific limits and extended-buffer behavior.

## Test Signals
Compile-time tests catch missing prototypes or constants. Runtime call-availability probes and successful high-level SCM operations validate that service IDs, command IDs, and argument metadata match firmware expectations.
