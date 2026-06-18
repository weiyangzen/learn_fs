# sources/distributed-fs/ceph-client/drivers/crypto/starfive/jh7110-cryp.h

## Purpose
This header defines the shared register layout, bitfields, limits, device state, transform state, and request state for the StarFive JH7110 crypto driver family. It is included by the platform driver and algorithm implementations for AES, hash, and RSA.

## Important APIs, types, and definitions
Top-level register offsets include `STARFIVE_ALG_CR_OFFSET`, FIFO, interrupt mask/flag, and DMA length registers. AES, hash, and PKA control/status words are represented as bitfield unions: `union starfive_aes_csr`, `union starfive_hash_csr`, `union starfive_pka_cacr`, and `union starfive_pka_casr`. These define mode encodings, busy/done bits, key-done bits, start/reset bits, hash modes for SM3/SHA2, HMAC flags, and PKA operation sizing.

`struct starfive_rsa_key` stores RSA components and bit lengths. `union starfive_alg_cr` controls top-level algorithm start, DMA enables, done, and clear. `struct starfive_cryp_ctx` is per-transform state shared by all algorithm types: device pointer, request context pointer, hash mode, key buffer, HMAC flag, RSA key, and fallback transforms. `struct starfive_cryp_dev` is per-device state: list node, device, clocks, reset, MMIO, physical base, DMA channels/configs, crypto engine, completion, request lengths, tags, auth size, flags, error, side-channel setting, and active request union. `struct starfive_cryp_request_ctx` is per-request state with CSR image, SG pointers, hash/digest metadata, AAD pointer, RSA scratch buffer, and fallback ahash request storage.

The header declares `starfive_cryp_find_dev()` and algorithm registration functions for hash, RSA, and AES.

## Control flow and state model
The platform driver fills `starfive_cryp_dev` at probe. Algorithm transform init stores a pointer in `starfive_cryp_ctx`. During request execution, algorithm files fill `starfive_cryp_request_ctx` and use the `req` union in `starfive_cryp_dev` to remember the active Crypto API request until the crypto engine callback finalizes it.

## Dependencies and integration points
The header depends on Crypto API AES/hash/SHA/SM3 constants, scatterwalk, Linux DMA mapping and DMAengine, interrupts, completions, and reset/clock-managed platform state through included headers. It is the ABI between `jh7110-cryp.c`, `jh7110-aes.c`, and the unlisted hash/RSA files.

## Risks
C bitfield layout for hardware CSRs can be compiler and endian sensitive; the driver writes the union's `u32 v` to MMIO, so target assumptions must match the hardware ABI. Shared request fields in `starfive_cryp_dev` make crypto engine serialization necessary. `MAX_KEY_SIZE` follows `SHA512_BLOCK_SIZE`, so AES, HMAC, and hash users share a broad key buffer. The flexible ahash fallback request at the end of `starfive_cryp_request_ctx` constrains request-size calculations.

## Test signals
Compile tests should cover all included algorithm files together. Runtime tests should validate CSR mode bits written by AES/hash/RSA paths, DMA completion behavior, fallback request sizing, side-channel flag propagation, tag buffers, and active request union use under serialized engine execution.
