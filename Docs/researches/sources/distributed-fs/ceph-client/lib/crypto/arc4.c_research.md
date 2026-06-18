# sources/distributed-fs/ceph-client/lib/crypto/arc4.c

## Purpose
This file implements the ARC4 stream cipher key-scheduling algorithm and pseudorandom generation/XOR routine for legacy users.

## Important APIs, Types, and Functions
It exports `arc4_setkey()` and `arc4_crypt()`, operating on caller-provided `struct arc4_ctx` containing `S[256]`, `x`, and `y`.

## Control Flow
`arc4_setkey()` initializes the permutation to identity, then runs the standard 256-step key scheduling loop cycling over the provided key. `arc4_crypt()` loads `x` and `y`, repeatedly swaps permutation entries, derives a keystream byte from `S[(a+b)&0xff]`, XORs input to output, and stores the updated indices back to the context.

## State and Persistence
The ARC4 permutation and indices persist in `struct arc4_ctx` across calls, so encryption/decryption continues the stream. There is no module-global mutable state.

## Dependencies and Integration Points
It depends on `<crypto/arc4.h>` and kernel export/module APIs. It is selected by `CRYPTO_LIB_ARC4`.

## Risks and Test Signals
ARC4 is cryptographically weak and should be legacy-only. Implementation risks include zero-length key assumptions, context reuse mistakes, and in-place pointer overlap expectations. Test signals are known ARC4 vectors, stream continuation tests, zero-length data calls, and in-place encryption/decryption.
