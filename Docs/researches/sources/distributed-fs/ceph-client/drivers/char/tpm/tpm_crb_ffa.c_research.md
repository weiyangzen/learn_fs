# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_crb_ffa.c

## Purpose
Implements the Arm FF-A TPM CRB start-method companion used by the generic CRB driver when a TPM service is exposed as an FF-A partition. It does not own the command buffer itself; it sends standardized direct-request messages to notify the secure service that CRB command or locality control fields changed.

## Important APIs, Types, And Functions
Exports `tpm_crb_ffa_init()` and `tpm_crb_ffa_start()`. Internal state is `struct tpm_crb_ffa`, holding the `ffa_device`, negotiated ABI version, a message mutex, and either direct-message v1 or v2 payload storage. `tpm_crb_ffa_to_linux_errno()`, `__tpm_crb_ffa_try_send_receive()`, `__tpm_crb_ffa_send_receive()`, `tpm_crb_ffa_get_interface_version()`, `tpm_crb_ffa_probe()`, and `tpm_crb_ffa_remove()` implement status mapping, retry, version negotiation, and FF-A driver lifetime.

## Control Flow
`tpm_crb_ffa_init()` registers the FF-A driver for built-in configurations and returns `-ENOENT` until probe completes, or `-ENODEV` after failed probe. Probe rejects partitions without direct receive support, allocates the singleton, selects 32-bit mode for AArch32 services, and verifies the service ABI via `CRB_FFA_GET_INTERFACE_VERSION`. `tpm_crb_ffa_start()` serializes on `msg_data_lock` and sends `CRB_FFA_START` with request type and locality. Message send retries `-EBUSY` until `busy_timeout_ms` expires.

## State And Persistence
State is a singleton pointer, negotiated major/minor version, and reusable FF-A message buffers. Nothing is persistent across driver unload; TPM command state lives in the CRB memory owned by the CRB driver and secure service.

## Dependencies And Integration Points
Depends on `linux/arm_ffa.h`, FF-A direct request/response operations, and the CRB driver through exported symbols declared in `tpm_crb_ffa.h`. It matches the TPM FF-A service UUID and translates service status codes to Linux errno values.

## Risks And Edge Cases
Only one FF-A TPM service instance is supported. The global singleton uses `ERR_PTR(-ENODEV)` to remember failed probe states. ABI compatibility checks are strict on major version and unusual on minor-version comparison, so version policy should be reviewed with DEN0138 changes. Timeout behavior depends on the module parameter and secure service returning `-EBUSY` consistently.

## Test Signals
Useful signals include FF-A service discovery, direct-request v1/v2 paths, AArch32 mode selection, busy retry timeout, incompatible ABI versions, duplicate service probe, CRB command start and locality start paths, and CRB driver retry behavior when `tpm_crb_ffa_init()` returns `-ENOENT`.
