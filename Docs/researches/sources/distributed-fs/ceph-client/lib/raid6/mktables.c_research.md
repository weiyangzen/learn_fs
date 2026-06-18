# sources/distributed-fs/ceph-client/lib/raid6/mktables.c

Purpose: host build tool that generates RAID6 Galois-field lookup tables.

Important APIs and flow: `gfmul()` implements GF(2^8) multiply with polynomial `0x1d`; `gfpow()` exponentiates using repeated squaring. `main()` prints C definitions for `raid6_gfmul`, nibble-vector `raid6_vgfmul`, `raid6_gfexp`, `raid6_gflog`, `raid6_gfinv`, and `raid6_gfexi`, plus kernel export directives.

State and persistence: output is generated source `tables.c` during the build; no runtime state in this tool.

Dependencies and integration: invoked by the RAID6 Makefile as a host program, and generated tables are used by scalar and SIMD recovery.

Risks and test signals: a table-generation error corrupts all RAID6 recovery math. Signals include deterministic generated output, RAID6 test vectors, and recovery tests for all failure positions.
