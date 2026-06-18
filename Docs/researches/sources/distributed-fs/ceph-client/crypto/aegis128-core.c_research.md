# sources/distributed-fs/ceph-client/crypto/aegis128-core.c

Purpose: implements the AEGIS-128 AEAD algorithm, with generic software processing and optional runtime SIMD registration. It handles key/authsize validation, associated-data processing, encryption/decryption, tag generation, tag verification, plaintext wiping on authentication failure, and module registration.

Important APIs, types, and functions: key structures are `struct aegis_state` and `struct aegis_ctx`. Important functions include `aegis128_do_simd()`, `crypto_aegis128_update*()`, `crypto_aegis128_init()`, `crypto_aegis128_process_ad()`, `crypto_aegis128_process_crypt()`, `crypto_aegis128_final()`, `crypto_aegis128_setkey()`, `crypto_aegis128_setauthsize()`, generic and SIMD encrypt/decrypt variants, and module init/exit.

Control flow and behavior: initialization mixes key, IV, and constants through repeated AEGIS updates. Associated data is consumed from scatterlists with partial-block buffering. Encryption/decryption walk payload through `skcipher_walk_aead_*`, processing full and partial blocks. Finalization folds associated-data and ciphertext lengths into the state for seven updates, then XORs state blocks into the tag. Decryption compares supplied tag by XORing into the computed tag; failure wipes produced plaintext before returning `-EBADMSG`.

State and persistence: the transform stores a 16-byte key in `struct aegis_ctx`; each request uses stack-local state and tag buffers. `have_simd` is a read-only-after-init static key enabled only when SIMD algorithm registration succeeds. No state persists beyond transform lifetime.

Dependencies and integration points: depends on AEAD core registration, `skcipher_walk`, scatterwalk, jump labels, kernel SIMD usability checks, and `aegis.h`/SIMD wrappers. It registers `aegis128-generic` and, when supported, `aegis128-simd` with higher priority.

Risks and correctness concerns: authentication failure must not expose plaintext, hence the explicit wipe pass. Partial AD and partial payload block handling are subtle. SIMD and generic paths must be bit-for-bit equivalent. The module exit unregisters SIMD based on current SIMD support; registration/unregistration conditions must match.

Test signals: AEGIS-128 AEAD vectors across auth sizes 8-16, empty AD/plaintext, partial blocks, unaligned buffers, in-place operation, forced generic path, SIMD path, auth failure wipe behavior, and crypto self-tests for both driver names.
