# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/ch_ipsec/chcr_ipsec.h

## Purpose
Defines the Chelsio inline IPsec module interface, module metadata, ULD context, IPsec work-request layout, ESN AAD/IV payload, and per-SA hardware key context state used by `chcr_ipsec.c`.

## Important APIs, Types, And Functions
The header declares module identity macros (`CHIPSEC_DRV_MODULE_NAME`, `CHIPSEC_DRV_VERSION`, `CHIPSEC_DRV_DESC`), `struct ipsec_uld_ctx`, `struct chcr_ipsec_req`, `struct chcr_ipsec_wr`, `ESN_IV_INSERT_OFFSET`, `struct chcr_ipsec_aadiv`, and `struct ipsec_sa_entry`.

`struct chcr_ipsec_req` embeds `ulp_txpkt`, `ulptx_idata`, `cpl_tx_sec_pdu`, and `_key_ctx` in the exact order emitted to hardware. `struct ipsec_sa_entry` stores hmac/auth control, ESN flag, encryption key length, key context length, auth size, key context header, salt, and key/GHASH material.

## Control Flow
No runtime control flow is defined here. The structures are populated by SA setup and TX work-request construction in `chcr_ipsec.c`.

## State And Persistence
`ipsec_uld_ctx` persists per attached cxgb4 lower-layer device while the ULD is active. `ipsec_sa_entry` persists per offloaded xfrm state until `xdo_dev_state_free`. Both are in-memory kernel objects; no external persistence exists.

## Dependencies And Integration Points
The header pulls in cxgb4 hardware, message, and ULD headers plus Chelsio crypto core/algo/header definitions. It is tightly coupled to firmware CPL/ULPTX layout and to the crypto helper definition of `_key_ctx`, `MAX_SALT`, AES key sizes, and key-context macros.

## Risks
Structure layout must match hardware work-request expectations; reordering or padding changes are unsafe. The key buffer is sized as `2 * AES_MAX_KEY_SIZE`, which must remain large enough for padded AES key material plus GHASH H. Module version/name strings are used in logging and module metadata and should stay aligned with Kconfig/Makefile naming.

## Test Signals
Compilation with the cxgb4 and Chelsio crypto include paths is the primary static signal. Runtime validation comes indirectly from successful IPsec SA setup and packet encryption/decryption interoperability.
