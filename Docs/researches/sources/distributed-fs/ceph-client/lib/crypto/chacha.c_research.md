# sources/distributed-fs/ceph-client/lib/crypto/chacha.c

## Purpose
Streaming ChaCha wrapper that selects generic or architecture-specific crypt and HChaCha implementations.

## Important APIs, Types, And Functions
Defines `chacha_crypt_generic()` and exports `chacha_crypt()` and `hchacha_block()`. Optional arch include may define `chacha_crypt_arch`, `hchacha_block_arch`, and `chacha_mod_init_arch`.

## Control Flow
The generic stream function repeatedly calls `chacha_block_generic()` to generate a 64-byte keystream block and XOR it into `dst`, then handles a final partial block. Public wrappers delegate to the selected arch or generic functions. Optional module init invokes arch initialization.

## State, Persistence, And Dependencies
The ChaCha state is caller-owned and its counter advances through block generation. A stack keystream block is used for generic XOR and is not explicitly wiped in this file. Dependencies include `crypto_xor_cpy`, module lifecycle helpers, and optional arch headers.

## Integration Points
Used by ChaCha20-Poly1305 and other in-kernel stream cipher consumers. Exports are GPL-only.

## Risks
Caller nonce/counter uniqueness is critical; this file provides no misuse resistance. Overlapping source and destination must match `crypto_xor_cpy()` expectations. Partial final blocks consume a full counter block.

## Test Signals
ChaCha20 RFC vectors, in-place and out-of-place XOR tests, partial lengths from 0 to 65, and arch/generic parity are important.
