<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/cast6_generic.c -->
# sources/distributed-fs/ceph-client/crypto/cast6_generic.c

## Purpose

`cast6_generic.c` implements CAST-256/CAST6 per RFC 2612 and registers the generic `cast6` cipher. It builds on the shared CAST S-boxes and provides exported helpers for other implementations.

## Important APIs, Types, and Flow

`__cast6_setkey()` requires key lengths divisible by four, pads to 32 bytes, reads eight big-endian key words, and runs 12 key-schedule iterations. Each iteration applies two `W()` octaves using fixed `Tm` and `Tr` constants, then extracts rotation and masking subkeys into `struct cast6_ctx`. `cast6_setkey()` adapts this to the Crypto API.

`__cast6_encrypt()` reads a 128-bit block, applies six forward `Q()` quad rounds followed by six reverse `QBAR()` quad rounds, and writes big-endian output. `__cast6_decrypt()` applies the inverse order. The registered `crypto_alg` exposes key bounds from `CAST6_MIN_KEY_SIZE` to `CAST6_MAX_KEY_SIZE`.

## State, Dependencies, and Integration

State is the expanded CAST6 context. Dependencies include `crypto/cast6.h`, unaligned accessors, and `cast_common.c` exported tables. The module registers names `cast6` and `cast6-generic` for block-mode consumers.

## Risks and Test Signals

Risks include accepting only 4-byte-multiple keys, subkey extraction order, Q/QBAR inversion, and shared table linkage. Test signals are RFC vectors, all valid key lengths, invalid non-multiple key rejection, decrypt/encrypt round trips, and generic-versus-accelerated equivalence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/cast6_generic.c -->
