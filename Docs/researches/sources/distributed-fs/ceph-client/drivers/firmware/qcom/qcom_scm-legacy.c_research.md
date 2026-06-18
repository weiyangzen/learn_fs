# sources/distributed-fs/ceph-client/drivers/firmware/qcom/qcom_scm-legacy.c

## Purpose
`qcom_scm-legacy.c` implements the pre-SMCCC Qualcomm SCM calling convention. It supports both buffered synchronous calls and a restricted atomic register-call format.

## Important APIs, Types, And Functions
- `struct arm_smccc_args` holds up to eight SMC registers.
- `struct scm_legacy_command` and `struct scm_legacy_response` define the shared command/response buffer layout.
- Layout helpers: `scm_legacy_command_to_response()`, `scm_legacy_get_command_buffer()`, and `scm_legacy_get_response_buffer()`.
- Transport helpers: `__scm_legacy_do()` loops through `QCOM_SCM_INTERRUPTED`.
- Public internal APIs: `scm_legacy_call()` and `scm_legacy_call_atomic()`.
- Global serialization: `qcom_scm_lock`.

## Control Flow
`scm_legacy_call()` builds a page-aligned command buffer containing header, little-endian arguments, response header, and response data space. It DMA maps the buffer, invokes SMC command class `1` with a context pointer and command physical address, maps secure monitor status through `qcom_scm_remap_error()`, then polls the response header until `is_complete` is set and copies up to three little-endian return values.

`scm_legacy_call_atomic()` builds a legacy atomic ID containing service, command, register class, IRQ mask, and argument count. It passes up to five arguments directly in registers and returns up to three result registers. It assumes the command is uninterruptible, atomic, and SMP-safe.

## State And Persistence
There is no long-lived per-call state beyond the global mutex. DMA command buffers are allocated and freed for each non-atomic call. Firmware may modify secure-world state depending on the service command invoked by callers.

## Dependencies And Integration Points
The file is called by `qcom_scm.c` when runtime convention probing selects `SMC_CONVENTION_LEGACY`. It depends on SMCCC SMC helpers, DMA mapping, endianness conversion, and the shared descriptor/result definitions in `qcom_scm.h`.

## Risks
Callers must flush/invalidate any additional buffers shared with secure world; this file only maintains the command/response buffer. Atomic calls `BUG_ON()` if too many arguments are provided. Polling `is_complete` has no timeout, so broken firmware can hang. The command layout uses 32-bit little-endian fields and can truncate if callers pass unsupported wide arguments under the legacy convention.

## Test Signals
Legacy platforms should complete convention probing and secure calls without falling back to SMCCC. Tests should cover non-atomic calls with arguments/results, interrupted SMC retry, and atomic boot/power operations. Hangs in response polling or `QCOM_SCM_INTERRUPTED` loops indicate firmware transport issues.
