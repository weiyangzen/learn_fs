# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_ftpm_tee.c

## Purpose
Implements a TPM 2.0 class device backed by Microsoft-compatible firmware TPM trusted application running in a GP-compliant OP-TEE environment.

## Important APIs, Types, And Functions
The TPM operation is `ftpm_tee_tpm_op_send()`, registered in `ftpm_tee_tpm_ops` with `TPM_OPS_AUTO_STARTUP`. Probe and removal are shared by both platform and TEE-client bindings through `ftpm_tee_probe_generic()` and `ftpm_tee_remove_generic()`. `ftpm_tee_match()` selects OP-TEE GP contexts, and module init registers both the platform and TEE client drivers.

## Control Flow
Probe allocates private state, opens a TEE context, opens a session to the fTPM TA UUID, allocates one shared memory buffer sized for command plus response, allocates a TPM chip, marks it TPM2 and synchronous, and registers it. Send validates command length, copies the TPM command into shared memory offset zero, invokes `FTPM_OPTEE_TA_SUBMIT_COMMAND`, reads the response from the second half of shared memory, validates the TPM header length against minimum, TA limit, and caller buffer, then copies it back.

## State And Persistence
Per-device state stores the TEE context, session id, shared memory handle, and TPM chip pointer. Persistent TPM NV state is owned by the TA/TEE implementation, not this driver.

## Dependencies And Integration Points
Depends on the Linux TEE client API, `tpm_chip_alloc()`, `tpm_chip_register()`, OF compatible `microsoft,ftpm`, and the OP-TEE fTPM TA UUID. Shutdown closes the TEE session and context for platform devices.

## Risks And Edge Cases
Shared memory is reused for all commands and assumes synchronous TPM core serialization. TA return values are passed back directly when invocation succeeds but TA status is nonzero. Response length is trusted only after header validation, but malformed short responses fail with `-EIO`. Probe must clean up partially opened TEE contexts and sessions in the correct order.

## Test Signals
OP-TEE TA discovery, platform and tee-client probe paths, command and response size limit tests, malformed response headers, TA invocation failure, removal/shutdown cleanup, and TPM2 startup/self-test through the TPM core.
