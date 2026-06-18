# sources/distributed-fs/ceph-client/drivers/firmware/qcom/qcom_scm-smc.c

## Purpose
`qcom_scm-smc.c` implements the modern Qualcomm SCM SMCCC transport for ARM 32-bit and 64-bit conventions, including extended argument buffers in TZMem and Qualcomm waitqueue handling.

## Important APIs, Types, And Functions
- `struct arm_smccc_args` holds eight SMC argument registers.
- `__scm_smc_do_quirk()` invokes `arm_smccc_smc_quirk()` with the Qualcomm A6 quirk and retries `QCOM_SCM_INTERRUPTED`.
- Waitqueue helpers: `fill_wq_resume_args()`, `scm_get_wq_ctx()`, and `__scm_smc_do_quirk_handle_waitq()`.
- Call executor: `__scm_smc_do()` serializes non-atomic calls, handles waitqueue sleep/resume, and retries `QCOM_SCM_V2_EBUSY`.
- Main API: `__scm_smc_call()` builds SMCCC call values and copies overflow arguments to TZMem.

## Control Flow
`__scm_smc_call()` encodes call type, 32/64-bit convention, owner, service, and command into `a0`, places `arginfo` in `a1`, and stores the first four arguments in registers. When more than four arguments are required, it allocates a TZMem buffer from SCM's pool, writes the remaining arguments as little-endian 32-bit or 64-bit values depending on convention, and passes its physical address in the last register argument.

Atomic calls invoke once through the quirk path. Non-atomic calls take `qcom_scm_lock`, run the waitqueue-aware call loop, release the lock, and retry `QCOM_SCM_V2_EBUSY` up to 20 times with 30 ms sleeps. If firmware returns `QCOM_SCM_WAITQ_SLEEP`, the code waits on the SCM waitqueue completion and resumes the secure call with `QCOM_SCM_WAITQ_RESUME`.

## State And Persistence
The transport has only the global mutex. Extended argument buffers are temporary TZMem allocations. Waitqueue sleep state is held by secure firmware and resumed through call context IDs supplied in firmware responses.

## Dependencies And Integration Points
This transport is used by `qcom_scm.c` for `SMC_CONVENTION_ARM_32` and `SMC_CONVENTION_ARM_64`. It depends on TZMem, SCM waitqueue completion APIs in `qcom_scm.c`, SMCCC helpers, DMA-safe memory, and shared SCM descriptor/error definitions.

## Risks
All extended-argument calls require an initialized SCM TZMem pool; otherwise they fail with `-EINVAL`. Waitqueue handling depends on IRQ/completion setup in SCM probe. Long or stuck firmware waitqueues can stall callers. Atomic callers bypass busy retry and waitqueue handling, so they must only use firmware calls that are safe in atomic context.

## Test Signals
Convention probing should select ARM32 or ARM64 on modern platforms. Extended-argument users such as memory assignment and HDCP should pass arguments correctly. Waitqueue-capable firmware can be tested by commands that sleep and later wake through SCM IRQ; failures show as waitqueue timeouts, invalid context warnings, or `GET_WQ_CTX` errors.
