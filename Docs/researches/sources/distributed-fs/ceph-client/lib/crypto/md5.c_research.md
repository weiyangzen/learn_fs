# sources/distributed-fs/ceph-client/lib/crypto/md5.c

## Purpose
Implements MD5 and HMAC-MD5 library functions, with a generic compression function and optional architecture-optimized block processing. This is compatibility crypto, not collision-resistant modern hashing.

## Important APIs, Types, and Functions
- Exports `md5_init()`, `md5_update()`, `md5_final()`, `md5()`, `hmac_md5_preparekey()`, `hmac_md5_init()`, `hmac_md5_init_usingrawkey()`, `hmac_md5_final()`, `hmac_md5()`, and `hmac_md5_usingrawkey()`.
- Uses `struct md5_ctx`, `struct md5_block_state`, `struct hmac_md5_key`, and `struct hmac_md5_ctx` from crypto headers.
- `md5_block_generic()` implements the four MD5 rounds through `F1`-`F4` and `MD5STEP()`.
- `__md5_final()` pads, appends bit length, runs the last block, and serializes state.

## Control Flow and State
`md5_update()` tracks total byte count, fills a 64-byte buffer, dispatches full blocks to `md5_blocks`, and leaves any tail buffered. `md5_final()` pads and zeroes the context. HMAC preparation hashes long keys if needed, XORs with ipad/opad, precomputes inner and outer MD5 states, and clears the derived key. HMAC final computes the inner digest into the working buffer, constructs the one-block outer padded input, finalizes with the precomputed outer state, and zeroes the HMAC context.

## Dependencies and Integration Points
Depends on `<crypto/md5.h>`, `<crypto/hmac.h>`, unaligned/endian helpers, word repeat helpers, and optional `$(SRCARCH)/md5.h` when `CONFIG_CRYPTO_LIB_MD5_ARCH` is enabled. Exported GPL symbols integrate with kernel subsystems still requiring MD5/HMAC-MD5.

## Risks and Test Signals
MD5 must not be used where collision resistance is required. Implementation risks include bytecount overflow semantics, padding boundary cases, endian conversion, and architecture hook equivalence. Tests should include RFC 1321 MD5 vectors, HMAC-MD5 vectors, zero-length input, inputs around 55/56/63/64/65 bytes, split-update equivalence, long HMAC keys, and generic-vs-arch block comparisons.
