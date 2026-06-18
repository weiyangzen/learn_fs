# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_fw_pke.h

## Purpose
`icp_qat_fw_pke.h` defines the public-key-engine firmware ABI used by RSA and Diffie-Hellman acceleration. It describes PKE request headers, source/destination parameter-table pointers, response headers, and status/valid flag helpers.

## Important APIs, Types, And Functions
Important structures are `icp_qat_fw_req_hdr_pke_cd_pars`, `icp_qat_fw_req_pke_mid`, `icp_qat_fw_req_pke_hdr`, `icp_qat_fw_pke_request`, `icp_qat_fw_resp_pke_hdr`, and `icp_qat_fw_pke_resp`. Macros include `ICP_QAT_FW_PKE_HDR_VALID_FLAG_SET()` and `ICP_QAT_FW_PKE_RESP_PKE_STAT_GET()`.

## Control Flow
PKE users zero a request, set the valid header flag, set service type to PKE, choose a firmware function ID, point `src_data_addr` and `dest_data_addr` at DMA parameter tables, set input/output parameter counts, store an opaque request pointer, and submit through a PKE transport ring. The callback decodes PKE status from response flags and uses the opaque value to complete the Crypto API request.

## State And Persistence Behavior
The header owns no state. Request and response structures are transient ring messages. Parameter tables and key buffers are caller-owned DMA mappings that must remain valid until callback completion.

## Dependencies And Integration Points
It includes `icp_qat_fw.h` and is used by `qat_asym_algs.c` for RSA encrypt/decrypt and DH public/shared-secret operations. It integrates the Linux akcipher/KPP APIs with QAT PKE firmware function IDs.

## Risks
PKE status is embedded in a common-response byte shifted out of `comn_resp_flags`, so decoding must use the PKE-specific macro. Parameter counts and table terminators must match the chosen firmware function ID or firmware will read bad addresses. The ABI assumes 64-bit DMA addresses in flat pointer tables.

## Test Signals
RSA and DH Crypto API selftests across supported key sizes should show valid PKE statuses. Negative tests should cover unsupported key sizes, too-small destination buffers, malformed keys, and firmware error responses.
