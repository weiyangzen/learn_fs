# sources/distributed-fs/lustre-release/lnet/lnet/adler.c

## Purpose
Registers an LNet crypto API synchronous hash implementation named `adler32` backed by `zlib_adler32`. It lets LNet checksum code access Adler-32 through the kernel shash interface.

## Important APIs and functions
`adler32_cra_init` initializes the transform context seed to 1. `adler32_setkey` accepts a 32-bit seed. `adler32_init`, `adler32_update`, `adler32_final`, `adler32_finup`, and `adler32_digest` implement the shash lifecycle. Static `struct shash_alg alg` declares names, priority, optional-key flag, block size, digest size, context sizes, and callbacks. Public `cfs_crypto_adler32_register` and `cfs_crypto_adler32_unregister` register/unregister the algorithm.

## Control flow
Registration passes `alg` to `crypto_register_shash`. A digest operation initializes descriptor state from the transform seed, updates it with one or more buffers through `zlib_adler32`, and writes the resulting 32-bit value to the caller output. `digest` and `finup` share `__adler32_finup`.

## State and persistence
State is limited to per-transform seed (`cra_ctxsize`) and per-descriptor running checksum (`descsize`). There is no persistent storage.

## Dependencies and integration points
Depends on Linux crypto internal hash APIs and zlib. Built into `lnet.o` by the LNet Makefile and exposed through `adler.h` for LNet crypto registration paths.

## Risks and test signals
Risks include unaligned `u32` stores/loads through `u8 *`, host-endian digest interpretation, incorrect seed size, and registration name conflicts. Tests should cover register/unregister, default seed digest against known Adler-32 vectors, keyed seed behavior, update-vs-digest equivalence, zero-length input, and repeated module load/unload.
