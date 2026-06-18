# sources/distributed-fs/ceph-client/drivers/crypto/bcm/spu.c

Purpose: SPU-M message-format implementation for Broadcom crypto hardware. It translates the common software-facing SPU parameters from `spu.h` into big-endian SPU-M request headers and provides helpers for payload limits, response parsing, padding, status handling, and CCM IV formatting.

Important APIs and functions: exports `hash_alg_name` and `aead_alg_name`; `spum_dump_msg_hdr()` decodes MH/SCTX/BDESC/BD fields for packet debug; `spum_ns2_ctx_max_payload()` and `spum_nsp_ctx_max_payload()` cap chunk sizes; `spum_payload_length()` reads response BD size; `spum_hash_pad_len()`, `spum_gcm_ccm_pad_len()`, `spum_assoc_resp_len()`, and `spum_digest_size()` implement hardware-specific sizing; `spum_create_request()` builds full AEAD/hash/cipher headers; `spum_cipher_req_init()` and `spum_cipher_req_finish()` split skcipher setup-time and request-time header work; `spum_request_pad()` materializes GCM/CCM, hash, and STATUS padding; `spum_status_process()` maps hardware status into `SPU_INVALID_ICV` or `-EBADMSG`; `spum_ccm_update_iv()` writes CCM B0 fields and plaintext length.

Control flow: caller computes common `spu_request_opts`, cipher/hash/AEAD parameters, then calls the sizing helpers and header builders. `spum_create_request()` computes auth/cipher lengths and offsets, writes the SPUHEADER, appends auth key, cipher key, IV, BDESC, and BD, and returns the exact header length. The skcipher fast path prebuilds stable SCTX/key fields at setkey time and later updates inbound/outbound, IV, BDESC, and BD size per request.

State and persistence: no durable storage. State is encoded into caller-provided DMA-able header buffers and into mutable `cipher_parms->iv_buf` for XTS and CCM. Debug output depends on global debug flags from `util.h`.

Dependencies and integration points: includes `spu.h`, `spum.h`, `cipher.h`, and `util.h`; uses Linux endian helpers, SHA constants, Crypto API naming, and the Broadcom request construction path used by the mailbox/DMA driver.

Risks: header length arithmetic assumes key and IV lengths are word-aligned where SCTX word counts are incremented by `/ 4`; BD size is 16-bit; AEAD decrypt subtracts digest size from cipher/auth lengths; RFC4543 overrides offsets in a special path; CCM may need word padding before ICV; XTS mutates IV state for SPU-M by zeroing the hardware IV and placing the tweak in payload. Status parsing is endian-specific.

Test signals: kernel crypto selftests for CBC/ECB/CTR/XTS, GCM, CCM, RFC4543/GMAC, HMAC/hash chunking, invalid ICV, empty hashes, and multi-chunk payloads should cover this file. Useful debug signals are packet header dumps, `SPU response STATUS`, and matching request/response payload lengths.
