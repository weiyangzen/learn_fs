# sources/distributed-fs/ceph-client/arch/sparc/lib/hweight.S

Purpose: SPARC64 population-count helpers.

Important APIs/functions: Exports `__arch_hweight8`, `__arch_hweight16`, `__arch_hweight32`, and `__arch_hweight64`.

Control flow: Uses the SPARC population-count instruction/sequence to count set bits in the requested operand width and returns the count.

State and persistence: Pure register computation.

Dependencies/integration: Includes `linux/export.h` and `linux/linkage.h`; used by generic bit-count APIs.

Risks/test signals: Width masking must match API expectations. Test zero, all-ones for each width, sparse bits, and random values against generic hweight.
