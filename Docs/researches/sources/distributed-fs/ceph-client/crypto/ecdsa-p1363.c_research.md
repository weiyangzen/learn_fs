# sources/distributed-fs/ceph-client/crypto/ecdsa-p1363.c

## Purpose
`ecdsa-p1363.c` registers the `p1363` signature template for ECDSA algorithms. It converts fixed-width IEEE P1363 signatures (`r || s`) into the internal `struct ecdsa_raw_sig` format and delegates verification to a child ECDSA signature algorithm.

## Important APIs, Types, And Functions
- `struct ecdsa_p1363_ctx` stores the spawned child `crypto_sig`.
- `ecdsa_p1363_verify()` checks signature length, converts `r` and `s` from big-endian byte strings to internal limbs, and calls `crypto_sig_verify()` on the child.
- `ecdsa_p1363_key_size()`, `ecdsa_p1363_max_size()`, and `ecdsa_p1363_digest_size()` proxy child metadata.
- `ecdsa_p1363_set_pub_key()` forwards public-key setup to the child.
- `ecdsa_p1363_create()` validates that the child algorithm name starts with `ecdsa`, names the instance, and registers it.

## Control Flow
The template is instantiated as `p1363(ecdsa-...)`. At transform init it spawns the child signature algorithm. Verification computes `keylen` from the child key size, requires exactly `2 * keylen` input bytes, imports both halves with `ecc_digits_from_bytes()`, then delegates to the underlying ECDSA verifier.

## State And Persistence
The transform context holds only the child `crypto_sig` pointer. Public key state is stored inside the child transform. Request state is stack-local.

## Dependencies And Integration Points
The file depends on the crypto sig template framework, `ecc_digits_from_bytes()`, and `ecdsa.c` raw signature verification. The template object `ecdsa_p1363_tmpl` is registered by `ecdsa.c`.

## Risks And Edge Cases
Length handling must match fixed-width P1363 encoding exactly. The template only checks the first five characters of the child name (`ecdsa`), so algorithm naming conventions matter. It does not parse ASN.1 or accept variable-width integers; that is the x962 template's role.

## Test Signals
`testmgr.h` includes P1363 ECDSA P-256 vectors and `testmgr.c` maps `p1363(ecdsa-nist-p*)` algorithms, with most larger/smaller curves covered by child tests. Useful tests include wrong-length signatures, leading-zero fixed-width values, public-key forwarding, and unsupported child algorithm rejection.
