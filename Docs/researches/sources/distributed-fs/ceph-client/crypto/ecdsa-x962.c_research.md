# sources/distributed-fs/ceph-client/crypto/ecdsa-x962.c

## Purpose
`ecdsa-x962.c` registers the `x962` signature template for ECDSA algorithms. It parses ASN.1 DER/BER `ECDSA-Sig-Value` signatures into raw `r` and `s` limbs before delegating verification to a child ECDSA algorithm.

## Important APIs, Types, And Functions
- `struct ecdsa_x962_ctx` stores the child `crypto_sig`.
- `struct ecdsa_x962_signature_ctx` holds a raw signature and digit count for ASN.1 callbacks.
- `ecdsa_get_signature_rs()` validates one ASN.1 INTEGER, strips a permitted leading zero, and imports it with `ecc_digits_from_bytes()`.
- `ecdsa_get_signature_r()` and `ecdsa_get_signature_s()` are ASN.1 decoder callbacks.
- `ecdsa_x962_verify()` runs `asn1_ber_decoder()` with `ecdsasignature_decoder`, then delegates to the child.
- `ecdsa_x962_max_size()` computes maximum DER encoding size including integer and sequence overhead.
- `ecdsa_x962_create()` validates an ECDSA child, configures proxy methods, and registers the instance.

## Control Flow
An `x962(ecdsa-...)` transform spawns its child on init. Verification computes digit count from child key size, decodes the ASN.1 signature into `sig_ctx.sig`, and calls `crypto_sig_verify()` on the child. Public key, key size, and digest size operations are forwarded to the child transform.

## State And Persistence
The wrapper transform persists only the child signature transform. Parsed signature state is request-local. Public key material is owned by the child.

## Dependencies And Integration Points
The file depends on generated ASN.1 decoder `ecdsasignature.asn1.h`, crypto sig templates, and ECC conversion helpers. The template object `ecdsa_x962_tmpl` is registered by `ecdsa.c`.

## Risks And Edge Cases
ASN.1 integer handling must reject negative encodings and oversized components while accepting one leading zero when needed to keep the integer positive. The decoder must populate both r and s; raw ECDSA verification performs range checks afterward. Maximum-size reporting differs for P-521 because coordinates do not need the extra positive-integer byte.

## Test Signals
`testmgr.h` includes x962 vectors for P-192, P-256, P-384, and P-521. Useful tests include malformed ASN.1 sequences, missing r or s, oversized INTEGERs, unnecessary/required leading zero cases, and invalid child algorithms.
