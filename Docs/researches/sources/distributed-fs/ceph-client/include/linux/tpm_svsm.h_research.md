# sources/distributed-fs/ceph-client/include/linux/tpm_svsm.h

## Purpose
Defines request and response helpers for AMD SVSM vTPM commands in SEV-SNP guests. It maps the SVSM vTPM command structure to the TCG TPM simulator protocol used for `TPM_SEND_COMMAND`.

## Important APIs, Types, And Functions
Exports `SVSM_VTPM_MAX_BUFFER`, `struct svsm_vtpm_request`, `struct svsm_vtpm_response`, `struct svsm_vtpm_cmd_request`, and `struct svsm_vtpm_cmd_response`. Inline helpers are `svsm_vtpm_cmd_request_fill()` and `svsm_vtpm_cmd_response_parse()`.

## Control Flow
`svsm_vtpm_cmd_request_fill()` verifies the TPM command payload fits within the fixed 4096-byte maximum minus request header, writes platform command `8`, locality, payload size, and copies the TPM command bytes. `svsm_vtpm_cmd_response_parse()` validates the caller output buffer is large enough, rejects oversized platform response lengths, copies the response bytes, and returns the response size.

## State, Persistence, And Dependencies
No persistent state is stored. The packed request layout is wire/ABI state shared with SVSM firmware. Dependencies are `errno`, `string`, and base integer types.

## Integration Points
Used by an SVSM-backed TPM transport driver as the adapter between Linux TPM core `send`/`recv` semantics and the SVSM call interface. It integrates with confidential-computing guest firmware rather than physical TPM buses.

## Risks And Test Signals
Risks include buffer-size mismatch with simulator protocol, untrusted platform response sizes, nonzero locality support assumptions, and layout padding mistakes. Test signals are request-size boundary tests at 4096 bytes, malformed response-size tests, packed layout assertions, and end-to-end TPM2 commands through an SVSM vTPM instance.
