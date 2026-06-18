# sources/distributed-fs/ceph-client/drivers/crypto/sa2ul.h

## Purpose
This header defines the SA2UL driver contract shared by `sa2ul.c`: register offsets, engine-enable bits, command label layout, security-context sizes and offsets, request subtype encoding, data-size limits, core device/transform/request structures, and algorithm ID enumerations. It is the hardware protocol map for the TI K3 SA2UL packet accelerator.

## Important APIs, types, and definitions
Key register definitions include `SA_ENGINE_STATUS` and `SA_ENGINE_ENABLE_CONTROL`, with enable bits for encryption, authentication, TRNG, PKA, context cache, and CPPI ports. Command label offsets such as `SA_CMDL_OFFSET_NESC`, `SA_CMDL_OFFSET_DATA_LEN`, and `SA_CMDL_OFFSET_OPTION_CTRL1` define the bytes patched into DMA metadata. `SA_MAX_DATA_SZ` caps hardware packets at `U16_MAX`, while `SA_UNSAFE_DATA_SZ_MIN` and `SA_UNSAFE_DATA_SZ_MAX` document the 240..255 byte fallback range.

`struct sa_crypto_data` holds per-device MMIO, match data, DMA pool, context ID bitmap, and RX/TX DMA channels. `struct sa_cmdl_param_info` and `struct sa_cmdl_upd_info` describe positions within command labels that are updated per request. `struct sa_ctx_info` owns one DMA security context, its physical address, command label template, update metadata, and EPIB words. `struct sa_tfm_ctx` aggregates encryption, decryption, and auth contexts plus fallback transforms. `struct sa_sha_req_ctx` embeds ahash fallback request storage. Enumerations `sa_ealg_id`, `sa_aalg_id`, and `sa_eng_algo_id` encode algorithm selection for security contexts and mode-control instruction tables.

## Control flow and state model
The header itself has no executable control flow, but it shapes all runtime behavior in `sa2ul.c`. Transform init allocates `sa_ctx_info` entries described here; setkey fills security context offsets such as `SA_CTX_ENC_KEY_OFFSET`; request execution patches fields described by `sa_cmdl_upd_info`; DMA callbacks decode request subtype fields such as `SA_REQ_SUBTYPE_ENC` and `SA_REQ_SUBTYPE_DEC`.

## Dependencies and integration points
The header depends on Crypto API AES/SHA constants and Linux bit/align conventions. It is included directly by `sa2ul.c` and indirectly constrains device tree matched hardware because DMA channel selection, context sizes, and engine IDs must match SA2UL firmware/hardware expectations.

## Risks
The definitions are protocol-sensitive: incorrect offsets or sizes corrupt command labels or security contexts. The duplicate `aux_key_info` field in `struct sa_cmdl_upd_info` in this snapshot is a direct compile risk. The `SA_MAX_NUM_CTX` bitmap and context ID macros must stay consistent with hardware limits. Unsafe-size constants are security and correctness relevant because the C file relies on them to avoid unpredictable hardware output.

## Test signals
Compile coverage is essential for this header. Runtime tests should validate context allocation up to `SA_MAX_NUM_CTX`, command label sizes never exceeding `SA_MAX_CMDL_WORDS`, fallback at unsafe sizes, correct IV indexes for AES-CBC and 3DES-CBC, and algorithm registration only for capabilities advertised by match data.
