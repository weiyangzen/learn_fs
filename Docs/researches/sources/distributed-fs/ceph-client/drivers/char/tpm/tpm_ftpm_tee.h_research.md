# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_ftpm_tee.h

## Purpose
Defines the fTPM OP-TEE command ids, shared-buffer limits, and private per-device structure used by `tpm_ftpm_tee.c`.

## Important APIs, Types, And Functions
Key definitions are `FTPM_OPTEE_TA_SUBMIT_COMMAND`, `FTPM_OPTEE_TA_EMULATE_PPI`, `MAX_COMMAND_SIZE`, `MAX_RESPONSE_SIZE`, and `struct ftpm_tee_private` containing the TPM chip, TEE session, TEE context, and shared memory object.

## Control Flow
The header has no executable flow, but it fixes the memory layout assumption used by the send path: command bytes at offset zero and response bytes at `MAX_COMMAND_SIZE`.

## State And Persistence
`struct ftpm_tee_private` is runtime state only. TA-side persistent TPM state is not represented in this header.

## Dependencies And Integration Points
Includes TEE, TPM, and UUID kernel headers. It is private to the fTPM TEE driver and mirrors the TA command ABI.

## Risks And Edge Cases
Command and response size constants must remain compatible with the TA. `FTPM_OPTEE_TA_EMULATE_PPI` is defined but unused by the current driver, so PPI behavior is not surfaced here.

## Test Signals
Compile coverage, shared memory size validation, and ABI compatibility checks with the matching OP-TEE fTPM TA.
