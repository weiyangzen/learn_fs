<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/camellia_generic.c -->
# sources/distributed-fs/ceph-client/crypto/camellia_generic.c

## Purpose

`camellia_generic.c` implements and registers the generic Camellia block cipher. It contains lookup tables, key schedules for 128/192/256-bit keys, block encryption/decryption routines, and a `crypto_alg` named `camellia`.

## Important APIs, Types, and Flow

`struct camellia_ctx` stores the key length and expanded key table. `camellia_set_key()` accepts only 16-, 24-, or 32-byte keys and dispatches to `camellia_setup128()`, `camellia_setup192()`, or `camellia_setup256()`. The 192-bit setup pads to 256 bits by appending the bitwise complement of the last 64 key bits.

The implementation uses precomputed SP tables, `CAMELLIA_F`, `CAMELLIA_FLS`, rotation macros, and `camellia_setup_tail()` to derive subkeys. `camellia_encrypt()` and `camellia_decrypt()` read 16-byte blocks as big-endian words, select 24 rounds for 128-bit keys or 32 rounds for 192/256-bit keys, call `camellia_do_encrypt()` or `camellia_do_decrypt()`, and write the swapped output halves.

## State, Dependencies, and Integration

Persistent state is the expanded key table in the transform context. The file depends on Crypto API cipher registration, unaligned big-endian helpers, and bit rotations. It integrates with block modes and template algorithms that request `camellia` or `camellia-generic`.

## Risks and Test Signals

Risks include key-schedule table indexing, half swapping, endian handling, and 192-bit complement padding. Tests should include official Camellia vectors for all key sizes, decrypt(encrypt()) round trips, alignment-sensitive inputs, mode-level tests, and equivalence with architecture-specific Camellia implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/camellia_generic.c -->
