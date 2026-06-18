# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sec2/sec_crypto.h

## Purpose
This header defines the SEC hardware-facing crypto descriptor contract used by `sec_crypto.c`. It contains algorithm, mode, key-size, address-type, and descriptor-type enums plus packed descriptor layouts for type2 and type3 SEC SQEs. It is the bitfield map that lets the Crypto API driver encode skcipher and AEAD operations for different hardware generations.

## Important APIs, Types, And Functions
The externally visible declarations are `sec_register_to_crypto()` and `sec_unregister_from_crypto()`. Core enums include `enum sec_calg` for 3DES/AES/SM4, `enum sec_hash_alg` for HMAC-SHA variants, `enum sec_cmode` for ECB/CBC/CTR/CCM/GCM/XTS, `enum sec_ckey_type`, `enum sec_bd_type`, `enum sec_auth`, `enum sec_cipher_dir`, and `enum sec_addr_type`.

`struct sec_sqe_type2` and `struct sec_sqe` describe the older type2 format nested inside the base SQE. `struct sec_sqe3` describes the newer type3 format with wider tags and rearranged fields. `struct bd_status` is an internal normalized completion view used by `sec_crypto.c` after parsing either descriptor format. Helper structs such as `bd3_auth_ivin`, `bd3_skip_data`, `bd3_stream_scene`, `bd3_no_scene`, `bd3_check_sum`, and `bd3_tls_type_back` model type3 union payloads.

## Control Flow
The header has no executable control flow, but it directly shapes runtime flow because descriptor fill functions in `sec_crypto.c` write these fields, and completion callbacks parse their status fields. Type2 descriptors use the nested `type2` fields under `struct sec_sqe`; type3 descriptors use `struct sec_sqe3` and carry the request pointer in `tag`.

## State And Persistence
There is no runtime state in this header. All state represented by these structs is transient descriptor state in DMA-visible command/completion memory. The layout uses little-endian integer types and packed/aligned attributes where required for hardware ABI stability.

## Dependencies And Integration Points
The header is included by `sec_crypto.c` and relies on kernel integer/endian types. It depends on `struct hisi_qm` being visible to compilation units through included SEC/QM headers. It is tightly coupled to SEC hardware manuals and to the field offsets in `sec_crypto.c`.

## Risks
Descriptor ABI drift is the primary risk. Incorrect bit comments, enum values, packing, or alignment would produce hardware-visible corruption. The two descriptor generations are similar enough that accidental cross-use is plausible, especially for address type, cipher/auth ordering, MAC length, and tag fields.

## Test Signals
Tests should cover both type2 and type3 devices or emulation. Descriptor dumps through QM debugfs, Crypto API known-answer tests, and negative AEAD ICV tests validate that bitfield packing matches hardware expectations. Sparse/endian builds are useful because the header uses explicit little-endian fields.
