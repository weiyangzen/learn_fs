# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/ch_ktls/chcr_common.h

## Purpose
Provides shared Chelsio kTLS crypto constants, AES-GCM key-context layout, and small TX ring helper inlines used by the kernel TLS offload implementation.

## Important APIs, Types, And Functions
The header defines kTLS/crypto constants such as `CHCR_MAX_SALT`, key size selectors, cipher/auth modes, TLS/generic protocol versions, `AES_BLOCK_LEN`, and key-context bitfield macros. `struct ktls_key_ctx` models the hardware key context containing header, salt, IV/auth word, and AES-GCM key/tag-sized storage. `FILL_KEY_CTX_HDR()` builds the big-endian key context header.

Queue helper inlines are `chcr_copy_to_txd()`, `chcr_txq_avail()`, `chcr_txq_advance()`, `chcr_eth_txq_stop()`, `chcr_sgl_len()`, and `chcr_flits_to_desc()`.

## Control Flow
There is no standalone control flow. kTLS TX code calls these helpers while building hardware work requests. `chcr_copy_to_txd()` copies data into a TX descriptor ring with wrap-around handling and pads to a 16-byte boundary. The queue helpers compute credits, advance producer state, stop netdev queues, compute DSGL flits, and convert flits to TX descriptors.

## State And Persistence
The header does not own state. It manipulates caller-owned `sge_txq`/`sge_eth_txq` runtime fields (`in_use`, `pidx`, queue stop count) and produces key-context words embedded in TX work requests. TLS key material persists wherever the kTLS implementation stores `ktls_key_ctx`.

## Dependencies And Integration Points
It includes `cxgb4.h` for SGE queue structures and constants. It is used by `chcr_ktls.c` and must remain consistent with firmware `CPL_TX_SEC_PDU` expectations and Linux TLS AES-GCM key sizes. The helper logic mirrors similar SGE functions in cxgb4/cxgb4vf transmit paths.

## Risks
Descriptor wrap and padding in `chcr_copy_to_txd()` are correctness-critical. Key-context bitfield macros must match firmware ABI and endian expectations. `chcr_flits_to_desc()` warns on exceeding `SGE_MAX_WR_LEN / 8`, but callers must still prevent oversized work requests. The key array size assumes AES-GCM 128/256 material and tag sizing used by Linux TLS definitions.

## Test Signals
Build coverage for `chcr_ktls.c`, TLS device add/delete, encrypted TLS TX with 128-bit and 256-bit AES-GCM, descriptor wrap stress, queue stop/restart behavior, and hardware packet authentication/decryption by a peer are practical validation signals.
