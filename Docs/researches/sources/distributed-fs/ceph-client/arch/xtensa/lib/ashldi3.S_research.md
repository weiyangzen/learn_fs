# sources/distributed-fs/ceph-client/arch/xtensa/lib/ashldi3.S

Purpose: Implements exported 64-bit arithmetic left shift helper `__ashldi3` for Xtensa.

Important APIs, types, and functions: `__ashldi3`, endian-dependent high/low word register aliases, `ssl`, `src`, `sll`, `abi_entry_default`, `abi_ret_default`, and `EXPORT_SYMBOL`.

Control flow: For shifts below 32, it uses shift-left plus `src` to combine high and low words. For shifts of 32 or more, it shifts the low word into the high word and zeros the low word.

State and persistence: Pure register computation, no memory state.

Dependencies and integration: Used by compiler-generated 64-bit shift operations and modules; depends on Xtensa shift amount register behavior and ABI register conventions.

Risks: Endian word assignment must match C 64-bit argument/return ABI; edge cases around shift counts near 32 are the primary correctness risk.

Test signals: Compiler runtime tests for signed/unsigned 64-bit left shifts at counts 0, 1, 31, 32, 33, and 63 on big- and little-endian builds.
