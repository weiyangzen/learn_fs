# sources/distributed-fs/ceph-client/scripts/crypto/gen-hash-testvecs.py

## Purpose
`gen-hash-testvecs.py` emits deterministic C test vectors for hashlib algorithms and kernel-specific hash/MAC primitives including AES-CMAC, GHASH, NH, Poly1305, POLYVAL, SHA3/SHAKE, and HMAC variants.

## Important APIs, Types, and Functions
`rand_bytes()` is a deterministic LCG used to reconstruct input data in kernel tests. Classes `AesCmac`, `Poly1305`, `Ghash`, and `Polyval` provide hash-like `update()` and `digest()` APIs. `hash_init()`, `compute_hash()`, and print helpers drive generic generation. Specialized generators include `gen_unkeyed_testvecs()`, `gen_hmac_testvecs()`, `gen_additional_sha3_testvecs()`, `gen_additional_blake2_testvecs()`, `gen_nh_testvecs()`, and all-ones stress cases for Poly1305, GHASH, and POLYVAL.

## Control Flow and State
The script requires exactly one algorithm argument, prints generated-file headers, dispatches by algorithm name, and writes C arrays/structs to stdout. State is local to each generated digest and deterministic from constants.

## Dependencies and Integration
It depends on Python 3, `hashlib`, `hmac`, and `cryptography` for AES-CMAC. It is integrated with kernel crypto test vector generation.

## Risks and Test Signals
Specialized algorithms are straightforward reference implementations, not optimized or hardened. Partial-block handling is intended only for final blocks. A formatting issue exists in `print_static_u8_array_definition()`: it prints `static const u8 {name} = {`, so callers include array dimensions in `name`. Test every dispatch path, reproducible diffs, boundary lengths in `DATA_LENS`, unsupported algorithms, and independent vector verification.
