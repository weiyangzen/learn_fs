# sources/distributed-fs/ceph-client/drivers/nvme/host/fc.h

## Purpose
This header provides common FC-NVMe Link Service definitions shared by the host FC transport and the target FC transport implementation. It wraps FC-NVMe request and response wire structures into aligned unions, provides helpers to format ACC/RJT response headers and Disconnect Association requests, defines validation error codes and human-readable names, and validates received Disconnect Association LS payloads.

## Important APIs, Types, And Functions
`union nvmefc_ls_requests` contains all supported host/target LS request shapes: generic word zero, Create Association, Create Connection, Disconnect Association, and Disconnect Connection. `union nvmefc_ls_responses` mirrors the response forms: RJT, Create Association accept, Create Connection accept, Disconnect Association accept, and Disconnect Connection accept. Both unions are aligned to 128 bytes so callers can allocate private data after them with predictable alignment.

Important inline helpers are `nvme_fc_format_rsp_hdr()`, `nvme_fc_format_rjt()`, `nvmefc_fmt_lsreq_discon_assoc()`, and `nvmefc_vldt_lsreq_discon_assoc()`. The file also defines validation error indexes (`VERR_*`), `validation_errors[]`, `NVME_FC_LAST_LS_CMD_VALUE`, and `nvmefc_ls_names[]`.

## Control Flow
The header has no independent runtime loop, but its helpers are called in the LS send and receive paths. Host-side disconnect transmission calls `nvmefc_fmt_lsreq_discon_assoc()` to populate request and response buffer pointers, timeout, descriptor list length, association descriptor, and disconnect command descriptor. Receive-side Disconnect Association handling calls `nvmefc_vldt_lsreq_discon_assoc()` before matching an association and formatting an accept.

Response formatting uses `nvme_fc_format_rsp_hdr()` for the common ACC/RJT prefix and `nvme_fc_format_rjt()` to add the reject descriptor. These helpers are used when rejecting unsupported, invalid, or temporarily unavailable LS requests.

## State And Persistence
The header allocates no dynamic state. It defines static string tables and constants compiled into every translation unit that includes it. The inline functions mutate caller-supplied LS buffers and therefore depend on the caller passing correctly sized `fcnvme_*` structures.

Because the validation error enum indexes into `validation_errors[]`, the order of both tables is a persistent source-level contract. FC-NVMe descriptor constants and endian conversions are wire ABI details; changes affect compatibility with targets and initiators.

## Dependencies And Integration Points
The header depends on FC-NVMe UAPI structures and constants such as `FCNVME_LS_*`, `FCNVME_LSDESC_*`, `fcnvme_lsdesc_len()`, `struct fcnvme_ls_rjt`, and disconnect descriptor layouts. It also depends on kernel endian helpers. It is included by `fc.c` and can be shared with target-side FC code so both sides use the same formatting and validation conventions.

## Risks
`nvme_fc_format_rjt()` passes `FCNVME_LSDESC_RQST` as the LS command argument to `nvme_fc_format_rsp_hdr()` rather than `FCNVME_LS_RJT`; this mirrors the current source but is a subtle field that deserves protocol-level scrutiny because a reject header with the wrong LS command would confuse peers. More generally, all helpers assume caller-provided buffers are large enough and aligned.

Validation is intentionally narrow for Disconnect Association. It checks length, descriptor list length, descriptor tags, descriptor lengths, and old-format scope, but it does not validate every reserved field. The static string tables are non-const `char *`, which is common in older kernel code but less robust than `const char * const`.

## Test Signals
Tests should serialize and inspect Disconnect Association requests, valid and invalid Disconnect Association receives, RJT formatting for unsupported LS commands, descriptor lengths after endian conversion, and each `VERR_*` mapping printed by `fc.c`. Interoperability tests with an FC-NVMe target are the strongest signal because this header encodes wire-format behavior.
