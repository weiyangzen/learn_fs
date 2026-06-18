# sources/distributed-fs/openafs/src/kauth/crypt.c

## Purpose
Provides a local DES-based Unix `crypt(3)` implementation for platforms that need it, specifically noted as used by the Andrew string-to-key path on Windows while Unix platforms use their system `crypt`. It implements classic and extended DES password hashing using generated permutation tables, DES key scheduling, salt handling, and base-64-style result encoding.

## Important APIs, Types, And Functions
The public entry point is `crypt(const char *key, const char *setting)`, returning a pointer to static `cryptresult`. Internal helpers include `des_setkey`, `des_cipher`, `init_des`, `init_perm`, optional `permute`, and debug-only `prtab`. `C_block` is the core packed 64-bit block representation. Static tables include DES IP, expansion, PC1/PC2, rotations, S-boxes, P32, CIFP, `itoa64`, `a64toi`, generated permutation tables, `SPE`, the key schedule `KS`, and `constdatablock`.

## Control Flow
`crypt` converts up to eight password bytes into a DES key block, initializes the DES tables lazily through `des_setkey`, handles extended settings beginning with `_` by folding additional password chunks through repeated encryption, parses iteration count and salt from the setting, encrypts a constant block with `des_cipher`, and encodes the resulting 64 bits into 11 printable characters after the copied salt prefix. `des_setkey` builds 16 key-schedule blocks using PC1/PC2 rotation permutations. `des_cipher` performs initial bit splitting/permutation, repeatedly runs the DES round function with salt-dependent swaps, then applies the final compression/permutation.

## State And Persistence
All state is process-local static memory: generated lookup tables, the key schedule, the readiness flag, and a single static result buffer. There is no disk persistence or locking. The returned pointer is overwritten by later calls and is not thread-safe.

## Dependencies And Integration Points
The file depends on `afsconfig.h`, `afs/param.h`, `roken.h`, and Windows headers. It is part of the kauth compatibility surface used by string-to-key code on Windows and must match expected Unix DES `crypt` behavior for legacy password/key derivation compatibility.

## Risks And Test Signals
The major risk is deliberate legacy cryptography: DES, small salts, static output buffers, and non-thread-safe global state. Portability risks come from byte-order/alignment-sensitive `C_block` use and `long` sizing. Test signals include known `crypt` test vectors, extended setting behavior, Windows Andrew string-to-key interoperability, repeated-call overwrite behavior, and builds across 32-bit and 64-bit Windows targets.
