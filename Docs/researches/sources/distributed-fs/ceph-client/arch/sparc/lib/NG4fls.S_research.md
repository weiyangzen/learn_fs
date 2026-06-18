# sources/distributed-fs/ceph-client/arch/sparc/lib/NG4fls.S

Purpose: Niagara4-specific find-last-set implementation.

Important APIs/functions: Defines `NG4fls` and `__NG4fls`.

Control flow: Uses SPARC integer bit operations to locate the highest set bit, with a public `fls`-style entry and an internal helper form. It returns zero for zero input and one-based bit position for nonzero input.

State and persistence: Pure register computation; no persistent state.

Dependencies/integration: Includes `linux/linkage.h`; patched into `fls` by `niagara4_patch_fls` when appropriate.

Risks/test signals: Off-by-one and zero-input behavior are the main risks. Test zero, powers of two, all-ones, and random 32-bit values against generic `fls`.
