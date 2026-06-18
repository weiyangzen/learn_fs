# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/qat_comp_req.h

## Purpose
`qat_comp_req.h` provides inline helpers for creating QAT compression/decompression firmware requests from prebuilt templates and for decoding common compression response fields.

## Important APIs, Types, And Functions
It defines `QAT_COMP_REQ_SIZE` and `QAT_COMP_CTX_SIZE`. Request builders are `qat_comp_create_req()`, `qat_comp_create_compression_req()`, and `qat_comp_create_decompression_req()`. Response accessors include consumed/produced counters, produced Adler32, opaque pointer, compression and translator error codes, compression and translator status bits, CNV flag, and uncompressed-block flag.

## Control Flow
`qat_comp_create_req()` copies a template into the request buffer, fills source/destination addresses and lengths, stores opaque data, sets compression length and output buffer size, and scales the ASB threshold by `slen >> 4`. Compression uses the first template in the context, while decompression advances one request-sized template. Completion code calls the response accessors to update `acomp_req`.

## State And Persistence Behavior
No state is owned here. The caller-owned compression context stores two request templates. Per-request buffers receive a copied template and are valid until firmware completion.

## Dependencies And Integration Points
It includes `icp_qat_fw_comp.h` and is used by `qat_comp_algs.c`. It bridges device-specific context builders with generic acomp request submission.

## Risks
The context is assumed to contain exactly two `icp_qat_fw_comp_req` templates in compression/decompression order. ASB threshold scaling mutates the copied request and depends on input length. Accessors assume response pointer points to a valid `icp_qat_fw_comp_resp`.

## Test Signals
Compression/decompression requests should show correct template selection, opaque recovery, length fields, and response counter decoding. Unit-style tests can compare generated request fields for representative source/destination sizes.
