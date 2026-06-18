# sources/distributed-fs/ceph-client/crypto/arc4.c

Purpose: registers the generic ARC4 stream cipher through the lightweight skcipher API. The implementation is intentionally compatibility-focused and warns callers that `ecb(arc4)` use is obsolete.

Important APIs/types/functions: `crypto_arc4_setkey()` delegates to `arc4_setkey()` for `struct arc4_ctx`. `crypto_arc4_crypt()` copies the transform context into the state IV buffer unless `CRYPTO_LSKCIPHER_FLAG_CONT` is set, then calls `arc4_crypt()`. `crypto_arc4_init()` emits a rate-limited obsolete-use warning. `arc4_alg` declares algorithm metadata, key bounds, state size, and symmetric encrypt/decrypt callbacks.

Control flow: module initialization registers `arc4_alg` with `crypto_register_lskcipher()`. Each operation either starts from the transform's base RC4 state or continues from the supplied state buffer, then mutates that working state as bytes are generated. Encrypt and decrypt are identical stream-XOR operations.

State and persistence: persistent state is per-transform `struct arc4_ctx`; per-request continuation state is passed through `siv`. There is no external persistence. Callers must preserve `siv` when using continuation mode.

Dependencies and integration points: depends on `crypto/arc4.h`, `crypto/internal/skcipher.h`, scheduler task names for warnings, and the lskcipher registration API. Exposes `"arc4"` / `"arc4-generic"` with alias `"ecb(arc4)"`.

Risks: ARC4 is cryptographically obsolete, and the warning confirms new users should avoid it. Continuation state misuse can restart keystreams or corrupt stream position. The implementation assumes the state buffer is large and aligned enough for `struct arc4_ctx`.

Test signals: key length bounds, encrypt/decrypt known-answer vectors, continuation versus fresh-state behavior, alias lookup, obsolete warning rate limiting, and module unregister behavior.
