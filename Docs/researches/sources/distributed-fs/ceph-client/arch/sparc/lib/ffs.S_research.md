# sources/distributed-fs/ceph-client/arch/sparc/lib/ffs.S

Purpose: SPARC64 find-first-set helpers.

Important APIs/functions: Exports `ffs` and `__ffs`.

Control flow: Handles zero specially for `ffs`, then uses bit tests/shifts to locate the least significant set bit. `ffs` returns one-based index or zero; `__ffs` returns zero-based index for nonzero input.

State and persistence: Pure register computation.

Dependencies/integration: Includes `linux/export.h` and `linux/linkage.h`.

Risks/test signals: Zero handling and one-based vs zero-based return contracts can be confused. Test zero, powers of two, all-ones, and random values against generic helpers.
