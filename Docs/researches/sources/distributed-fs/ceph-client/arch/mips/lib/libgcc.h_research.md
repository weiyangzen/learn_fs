# sources/distributed-fs/ceph-client/arch/mips/lib/libgcc.h

Purpose: declares endian-aware unions and integer-mode typedefs used by MIPS in-kernel libgcc helper implementations.

Important APIs/types/functions: defines `word_type`, `struct DWstruct`, `DWunion`, and for 64-bit MIPS R6 `ti_type`, `struct TWstruct`, and `TWunion`.

Control flow: compile-time endian branches place high/low words in ABI-correct order; unsupported endian emits preprocessor error.

State and persistence: type definitions only.

Dependencies and integration: included by `multi3.c` and potentially other compiler-runtime helpers.

Risks: field order must match target endian/ABI, or compiler helper arithmetic returns incorrect values.

Test signals: endian build coverage and helper tests for multiword arithmetic.
