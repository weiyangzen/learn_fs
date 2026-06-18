<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/cast5_generic.c -->
# sources/distributed-fs/ceph-client/crypto/cast5_generic.c

## Purpose

`cast5_generic.c` implements CAST-128/CAST5 per RFC 2144 and registers the generic `cast5` cipher. It includes CAST5-specific S-boxes, key schedule, and block encryption/decryption functions.

## Important APIs, Types, and Flow

The file uses shared `cast_s1` through `cast_s4` from `cast_common.c` plus local S-boxes `s5`, `s6`, `s7`, and `sb8`. `cast5_setkey()` pads the key to 128 bits, records reduced-round mode for keys up to 80 bits, runs `key_schedule()` twice to generate masking subkeys `Km` and rotation subkeys `Kr`, and stores them in `struct cast5_ctx`.

`__cast5_encrypt()` and `__cast5_decrypt()` are exported helpers. They parse 64-bit blocks as big-endian halves and apply the CAST F1/F2/F3 functions in the specified round order. Reduced-round mode skips the final four rounds. Wrapper functions adapt those helpers to the `crypto_alg` block cipher interface.

## State, Dependencies, and Integration

State is the expanded `cast5_ctx`, including `Km`, `Kr`, and reduced-round flag. Dependencies are unaligned accessors, `crypto/cast5.h`, and the exported shared CAST S-boxes. It integrates with Crypto API cipher consumers by registering `cast5` and `cast5-generic`.

## Risks and Test Signals

Risks include reduced-round threshold errors, key padding, byte extraction in the key schedule, and dependence on `cast_common` exports. Tests should include RFC 2144 vectors, 40- to 128-bit keys, reduced-round coverage, decryption inverse checks, and comparisons with accelerated CAST5 implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/cast5_generic.c -->
