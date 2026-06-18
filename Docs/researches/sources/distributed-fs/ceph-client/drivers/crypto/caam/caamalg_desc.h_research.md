# sources/distributed-fs/ceph-client/drivers/crypto/caam/caamalg_desc.h

## Purpose

`caamalg_desc.h` is the public descriptor-construction contract for CAAM AEAD and skcipher algorithm frontends. It publishes conservative descriptor text length macros and prototypes for the constructors implemented in `caamalg_desc.c`. The header lets callers size shared descriptor buffers, run inline-key fit calculations, and call the right constructor for generic authenc, GCM, IPsec GCM/GMAC, ChaCha-Poly, skcipher, XTS, protected blob, and protected-key job descriptor paths.

## Important APIs, constants, and types

- `DESC_AEAD_*`, `DESC_QI_AEAD_*`, and `DESC_AEAD_CTR_RFC3686_LEN` size generic authenc descriptors, including QI variants and extra RFC3686 nonce/counter commands.
- `DESC_AEAD_NULL_*` sizes null-encryption HMAC AEAD descriptors.
- `DESC_GCM_*`, `DESC_QI_GCM_*`, `DESC_RFC4106_*`, `DESC_QI_RFC4106_*`, `DESC_RFC4543_*`, and `DESC_QI_RFC4543_*` size GCM, IPsec GCM, and IPsec GMAC descriptors.
- `DESC_SKCIPHER_*` sizes shared skcipher descriptors.
- `KEYMOD` is the fixed key modifier string used by protected blob decapsulation descriptors.
- The constructor prototypes accept caller-owned `u32 *desc` buffers, `struct alginfo` key/algorithm descriptors, sizes such as `ivsize` and `icvsize`, mode flags such as `is_qi`, `geniv`, and `is_rfc3686`, SEC era, and DMA addresses for job/protected-key descriptors.

The header intentionally does not define `struct alginfo`; it relies on callers already including the CAAM descriptor-construction type definitions.

## Control flow and usage

Callers typically use this header in three steps:

1. Choose an algorithm entry and compute key/auth/IV attributes.
2. Use the `DESC_*` size macros with `desc_inline_query()` or fixed buffer sizing to decide whether keys can be embedded inline while keeping job plus shared descriptors within CAAM descriptor limits.
3. Populate `struct alginfo` and call a constructor to write the final descriptor words into per-transform buffers.

For QI users, the `DESC_QI_*` macros add the extra descriptor words needed to consume QI frame metadata such as assoclen and IV. For RFC3686 authenc, callers add `DESC_AEAD_CTR_RFC3686_LEN` to the base descriptor estimate because nonce/counter setup is not included in the base AEAD macro.

## State and persistence behavior

The header has no runtime state. Its constants become compile-time sizing rules and its prototypes define how C modules share descriptor-building behavior. The `KEYMOD` string is compiled into protected blob descriptors through `cnstr_desc_protected_blob_decap()`.

## Dependencies and integration points

This header depends on CAAM command sizing (`CAAM_CMD_SZ`), CAAM/DMA types (`u32`, `dma_addr_t`), and `struct alginfo`, all supplied by surrounding CAAM kernel headers. It is included by `caamalg_desc.c` and by algorithm frontends such as `caamalg_qi.c`. Its exported API is internal to the CAAM driver/module but uses `EXPORT_SYMBOL` implementations so multiple compilation units can link to the constructor functions.

The macros directly influence `DESC_MAX_USED_BYTES` and descriptor inline-key decisions in QI code. If the estimates are too small, the driver may overrun the hardware descriptor buffer or incorrectly inline key material; if too large, it may unnecessarily fall back to DMA key loads.

## Risks and edge cases

- Descriptor length macros must track exact constructor growth. Any new command in `caamalg_desc.c` should be reflected here or callers can under-allocate buffers.
- QI and non-QI variants are separated by macro name, so callers must choose the variant matching the constructor's `is_qi` flag.
- `DESC_AEAD_CTR_RFC3686_LEN` has a note that the nonce is counted in `cdata.keylen`; callers must coordinate key layout and sizing.
- `KEYMOD` is a protocol input for protected blobs. Changing it would break compatibility with blob decapsulation semantics.
- The header declares constructors for features not necessarily registered by every frontend; hardware capability checks remain the caller's responsibility.

## Test signals

Compile-time coverage should catch missing declarations and type mismatches. Runtime tests should verify descriptor construction for maximum-size keys, QI inline-key boundary cases, RFC3686 key-plus-nonce lengths, and every `DESC_*` length used in `desc_inline_query()`. A useful regression signal is that CAAM crypto algorithm registration succeeds and kernel crypto self-tests do not report descriptor length or invalid command failures across supported SEC eras.
