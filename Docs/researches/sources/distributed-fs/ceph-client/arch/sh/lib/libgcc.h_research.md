# sources/distributed-fs/ceph-client/arch/sh/lib/libgcc.h

Purpose: shared declarations/macros for SH libgcc-compatible helper assembly/C code.

Important content: includes byte-order definitions and helper-oriented type/ABI assumptions used by arithmetic routines.

Control flow: header-only; no runtime control flow.

State and persistence: no mutable state.

Dependencies and integration: included by SH libgcc helper implementations that need consistent endian handling and compiler ABI compatibility.

Risks: changing helper declarations or endian assumptions can desynchronize assembly helpers from compiler-generated calls.

Test signals: successful build of lib helpers and arithmetic runtime tests on both endian configurations.
