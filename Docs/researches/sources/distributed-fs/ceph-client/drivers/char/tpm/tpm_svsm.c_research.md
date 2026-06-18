# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_svsm.c

## Purpose
Implements an AMD SVSM vTPM driver for SEV-SNP guests, forwarding TPM commands to a Secure VM Service Module using the SVSM vTPM protocol.

## Important APIs, Types, And Functions
Private state is `struct tpm_svsm_priv` with one page-sized contiguous buffer. TPM callback `tpm_svsm_send()` uses `svsm_vtpm_cmd_request_fill()`, `snp_svsm_vtpm_send_command()`, and `svsm_vtpm_cmd_response_parse()`. Probe and remove are `tpm_svsm_probe()` and `tpm_svsm_remove()`.

## Control Flow
Probe allocates private state and one page buffer, allocates a managed TPM chip, stores private state on the chip device, marks the chip synchronous, probes TPM2 capabilities, registers the chip, and logs TPM version. Send formats command plus SVSM header into the internal physically contiguous buffer, performs the SVSM call in place, and parses the response back into the caller buffer.

## State And Persistence
Runtime state is the one-page command/response buffer. vTPM persistent state is owned by the SVSM.

## Dependencies And Integration Points
Depends on `linux/tpm_svsm.h`, `asm/sev.h`, a platform device named `tpm-svsm`, and TPM core registration.

## Risks And Edge Cases
The maximum buffer is one page; oversized TPM commands rely on the SVSM helper to reject them. The same buffer is reused for command and response. The driver is registered with `module_platform_driver_probe()`, so runtime unbind is intentionally unsupported and remove is exit-only.

## Test Signals
SEV-SNP guest discovery, one-page command limit, malformed SVSM responses, TPM2 probe, module unload, and SVSM call error propagation.
