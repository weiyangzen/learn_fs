# sources/distributed-fs/ceph-client/drivers/crypto/aspeed/aspeed-hace-crypto.c

## Purpose

`aspeed-hace-crypto.c` implements the symmetric cipher half of the Aspeed HACE driver. It registers asynchronous kernel-only AES, DES, and 3DES skcipher algorithms for AST2500 and AST2600, using the HACE crypto engine and software fallback for unsupported or malformed requests. AST2500 uses a coherent bounce buffer, while AST2600 can drive hardware scatter-gather descriptors for source and destination.

## Important APIs, Types, And Functions

The file centers on `struct aspeed_cipher_ctx`, `struct aspeed_cipher_reqctx`, and the shared `struct aspeed_engine_crypto` from `aspeed-hace.h`. `aspeed_crypto_do_request()` is the crypto-engine callback. `aspeed_hace_skcipher_trigger()` prepares the context/key/IV area and dispatches to `aspeed_sk_start()` or `aspeed_sk_start_sg()`. `aspeed_aes_crypt()` and `aspeed_des_crypt()` validate mode lengths and construct command bits; `aspeed_aes_setkey()` and `aspeed_des_setkey()` validate/cache keys and configure fallbacks. Registration exports ECB/CBC AES/DES/3DES on all versions and CTR AES/DES/3DES on AST2600.

## Control Flow

Encrypt/decrypt callbacks fill `rctx->enc_cmd` and queue the request. The crypto-engine worker marks the hardware busy and calls the selected start function. The trigger writes the context DMA address, copies IVs for CBC/CTR-like modes, copies keys after the IV area, enables interrupts, and starts either bounce-buffer or SG processing. Bounce mode copies input sg data into `cipher_addr`, programs source/destination to the same DMA buffer, and copies results back on completion. SG mode maps the caller scatterlists, builds HACE SG descriptors with the last bit in the final length field, programs hardware, then unmaps on interrupt-driven completion.

## State And Persistence Behavior

Transform state stores the key, key length, fallback skcipher, and start callback. Request state stores command bits and mapped sg counts. The device crypto engine stores one active request, coherent context buffer, source descriptor/input buffer, optional AST2600 destination descriptor buffer, resume callback, and busy flag. CBC/DES IV state is updated from the hardware context buffer when the request completes. DMA mappings are per request and are released in the resume path or on setup failure.

## Dependencies And Integration Points

The code depends on the parent HACE platform driver for MMIO, IRQ, DMA buffers, version selection, and crypto-engine allocation. It integrates with Linux skcipher/crypto-engine APIs, DES/AES key validation, DMA mapping, scatterlist helpers, and the HACE register/command definitions in `aspeed-hace.h`. Software fallback is allocated by algorithm name and used for AST2500 zero-length or block-unaligned requests.

## Risks And Test Signals

Risks include descriptor overflow relative to the fixed 0xa000 coherent buffers, incomplete unmap on SG errors, AST2500 fallback behavior differing from AST2600, IV update offsets for DES versus AES, CTR edge cases with non-block-sized input, and silent registration failures because register loops only log errors. Test with `tcrypt`/crypto selftests for AES/DES/3DES ECB/CBC/CTR, in-place and out-of-place SGs, unaligned lengths, zero-length requests, large fragmented scatterlists, fallback paths, and interrupt-with-no-busy warnings.
