# sources/distributed-fs/ceph-client/crypto/ecrdsa.c

## Purpose
`ecrdsa.c` implements EC-RDSA (GOST R 34.10 family) signature verification as a crypto sig algorithm. It parses GOST public-key ASN.1 metadata, selects a GOST curve and Streebog digest size, validates the public key, and verifies raw EC-RDSA signatures.

## Important APIs, Types, And Functions
- `struct ecrdsa_ctx` stores algorithm, curve, and digest OIDs; selected `ecc_curve`; digest metadata; raw public key pointer/length; and public point storage.
- `get_curve_by_oid()` maps supported GOST curve OIDs to constants from `ecrdsa_defs.h`.
- `ecrdsa_verify()` performs the EC-RDSA verification equation using little-endian digest import and big-endian signature import.
- ASN.1 callbacks `ecrdsa_param_curve()`, `ecrdsa_param_digest()`, and `ecrdsa_parse_pub_key()` fill context fields during public-key parsing.
- `ecrdsa_set_pub_key()` decodes `SubjectPublicKeyInfo`, reads appended algorithm parameters, determines Streebog-256 or Streebog-512, parses curve parameters, imports public coordinates, and validates the point.
- `ecrdsa_alg` registers `ecrdsa` / `ecrdsa-generic`.

## Control Flow
Public-key setup first decodes the public-key wrapper, then reads two appended `u32` values for algorithm OID and parameter length. It selects digest metadata from algorithm OID, decodes parameters to identify curve and optional digest OID, enforces curve/digest/key length consistency, imports the two public coordinates from little-endian order, and performs partial point validation.

Verification checks that curve, digest, signature, and public key sizes are consistent. It imports signature `s` and `r`, validates `0 < r,s < q`, imports digest as little-endian `e = h mod q` with zero mapped to one, computes `v = e^-1`, `z1 = s*v mod q`, and `z2 = -r*v mod q`, then computes `z1*G + z2*Q` and compares x modulo q to r.

## State And Persistence
The transform context persists parsed public-key metadata and point storage. It stores `ctx->key` as a pointer into decoded key input during setup, then imports coordinates into owned `_pubp` storage. No signing or private state is held.

## Dependencies And Integration Points
The file depends on generated ASN.1 decoders `ecrdsa_params.asn1.h` and `ecrdsa_pub_key.asn1.h`, OID registry constants, Streebog digest sizes, shared ECC arithmetic, and curve constants from `ecrdsa_defs.h`.

## Risks And Edge Cases
The code supports selected GOST curve OIDs only and returns `-ENOPKG` for unsupported algorithms or mismatched sizes. It uses partial public-key validation, not full order validation, because these are GOST signature curves. The appended-parameter parsing after `key + keylen` is unusual and relies on the caller/key parser contract. Endianness differs between signature, digest, and public-key fields, making conversion tests important.

## Test Signals
`testmgr.h` includes `ecrdsa_tv_template` and `testmgr.c` maps `ecrdsa` to signature tests. Useful tests include unsupported OIDs, digest OID mismatch, invalid point coordinates, wrong signature length, zero or out-of-range r/s, and both 256-bit and 512-bit curve families.
