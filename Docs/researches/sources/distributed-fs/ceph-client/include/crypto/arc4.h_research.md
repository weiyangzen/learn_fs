# sources/distributed-fs/ceph-client/include/crypto/arc4.h

Purpose: ARC4 stream cipher constants, context, and primitive operations.

Important APIs/types/functions: key/block size macros, `struct arc4_ctx`, `arc4_setkey`, and `arc4_crypt`.

Control flow: caller initializes permutation state with `arc4_setkey`, then encrypts/decrypts by XORing the generated keystream via `arc4_crypt`.

State and persistence: `arc4_ctx` contains mutable S-box and indices `x/y`; encryption advances state.

Dependencies and integration points: lightweight primitive used by legacy crypto users.

Risks: ARC4 is cryptographically obsolete for new designs; state reuse or weak keys are severe. Context is mutable and not reusable concurrently without locking/copying.

Test signals: ARC4 known-answer tests, streaming split equivalence tests, and deprecation policy checks for new users.
