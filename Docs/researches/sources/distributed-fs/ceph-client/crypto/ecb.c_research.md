# sources/distributed-fs/ceph-client/crypto/ecb.c

## Purpose
`ecb.c` registers the `ecb` lskcipher template. It wraps either modern lskcipher algorithms or older raw single-block cipher algorithms to provide Electronic Codebook mode with no IV.

## Important APIs, Types, And Functions
- `crypto_ecb_crypt()` runs a raw cipher block function over complete blocks and returns leftover bytes unless the final flag requires strict block alignment.
- `crypto_ecb_encrypt2()` and `crypto_ecb_decrypt2()` adapt legacy `crypto_cipher` children to lskcipher operations.
- `lskcipher_alloc_instance_simple2()` and associated init/exit/setkey/free helpers implement fallback wrapping for legacy cipher algorithms.
- `crypto_ecb_create()` first tries `lskcipher_alloc_instance_simple()` and falls back to the legacy helper. It rejects lskcipher children that already have an IV.
- `crypto_ecb_tmpl` registers the `ecb` template.

## Control Flow
For modern lskcipher children, `crypto_ecb_create()` builds a template instance that mostly forwards setkey, encrypt, decrypt, init, and exit to the child while forcing `ivsize = 0`. For raw cipher fallback, the wrapper spawns a `crypto_cipher`, sets inherited flags on setkey, and calls the child's block encrypt/decrypt function in a loop. Non-final partial input is reported as unconsumed bytes; final partial input is `-EINVAL`.

## State And Persistence
State is transform-local and consists of the child lskcipher or raw cipher pointer and child context. ECB has no IV or per-request chaining state.

## Dependencies And Integration Points
The file depends on internal cipher and lskcipher template helpers. It is a core mode used by many block ciphers and by higher-level modes that depend on raw block encryption. Testmgr includes `ecb(aes)`, `ecb(des)`, `ecb(des3_ede)`, and many other `ecb(...)` vectors.

## Risks And Edge Cases
ECB is cryptographically unsafe for structured multi-block plaintexts, but it remains a primitive/template. The code must handle two child API families consistently. A notable implementation risk is instance cleanup on the path where a modern child with nonzero IV is rejected; it returns `-EINVAL` after allocation, so cleanup behavior should be reviewed if this code is changed. Partial-block handling depends on the lskcipher final flag.

## Test Signals
Testmgr maps many ECB algorithms to cipher vectors. Useful tests cover legacy raw cipher wrapping, lskcipher child wrapping, final partial-block rejection, non-final partial return length, no-IV behavior, and inherited flag propagation during setkey.
