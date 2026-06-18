# sources/distributed-fs/ceph-client/arch/xtensa/lib/bswapdi2.S

Purpose: Implements exported 64-bit byte swap helper `__bswapdi2`.

Important APIs, types, and functions: `__bswapdi2`, `ssai`, `srli`, repeated `src` byte rotation/extraction sequence, ABI macros, and `EXPORT_SYMBOL`.

Control flow: Reverses byte order within each 32-bit half, then swaps the two halves by moving the transformed original low word to the high return register and vice versa.

State and persistence: Pure register transform.

Dependencies and integration: Used by compiler builtins or kernel byteorder operations when a helper call is emitted.

Risks: Return register order must match endian ABI; no memory fault risk, but subtle byte permutation bugs affect networking/storage data interpretation.

Test signals: `__builtin_bswap64` tests and kernel byteorder self-tests for values with distinct bytes on both endian configurations.
