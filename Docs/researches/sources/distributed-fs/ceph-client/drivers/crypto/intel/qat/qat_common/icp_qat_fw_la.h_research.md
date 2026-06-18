# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/icp_qat_fw_la.h

## Purpose
`icp_qat_fw_la.h` defines the lookaside crypto firmware ABI for bulk cipher, auth, cipher-hash, hash-cipher, TRNG, key-derive, MGF1, and precompute requests. It supplies request layouts, content descriptor control headers, service-specific flags, cipher/auth parameter blocks, and response layout.

## Important APIs, Types, And Functions
Key command IDs are in `icp_qat_fw_la_cmd_id`. Important structures include `icp_qat_fw_la_bulk_req`, `icp_qat_fw_cipher_req_hdr_cd_pars`, `icp_qat_fw_cipher_auth_req_hdr_cd_pars`, `icp_qat_fw_cipher_cd_ctrl_hdr`, `icp_qat_fw_auth_cd_ctrl_hdr`, `icp_qat_fw_cipher_auth_cd_ctrl_hdr`, `icp_qat_fw_la_cipher_req_params`, `icp_qat_fw_la_auth_req_params`, and `icp_qat_fw_la_resp`. Macros build and mutate LA flags for IV pointer/data mode, content descriptor offset, partial state, protocol, auth compare/return, digest-in-buffer, update-state, ZUC/GCM, and slice type.

## Control Flow
Runtime users build a common bulk request, choose a command (`CIPHER`, `CIPHER_HASH`, or `HASH_CIPHER` in this subset), fill content descriptor address and size, program current/next slice IDs, fill cipher/auth request parameters, and submit through transport. Completion decodes the common crypto status from `icp_qat_fw_la_resp`.

## State And Persistence Behavior
The header owns no state. It defines firmware-visible request fields copied into per-request buffers and content descriptor control fields that describe caller-owned DMA content descriptors. For multi-part operations, partial/update flags can represent firmware state progression, though this subset mainly uses non-partial requests.

## Dependencies And Integration Points
It includes `icp_qat_fw.h` and is consumed by `qat_algs.c` for AEAD and skcipher request setup. It bridges Linux Crypto API parameters, QAT hardware cipher/auth setup blocks from `icp_qat_hw.h`, and ETR transport messages.

## Risks
The hash/cipher control headers overlap in the same request `cd_ctrl` memory, so offsets and current/next IDs must match the chosen command chain. Packed auth params require exact offsets. Incorrect digest-in-buffer or compare-auth flags can turn encryption into invalid authentication behavior. AES-GCM/CCM AAD limit constants are protocol-specific.

## Test Signals
Crypto selftests for authenc HMAC-CBC-AES and AES CBC/CTR/XTS validate request parameters and response status handling. Descriptor dumps should show correct slice chains: cipher->auth for encrypt and auth->cipher for decrypt.
