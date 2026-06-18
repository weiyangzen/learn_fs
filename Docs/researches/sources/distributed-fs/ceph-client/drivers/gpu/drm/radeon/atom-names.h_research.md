# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/atom-names.h

Purpose: This header provides debug-only string tables for ATOM BIOS operation, table, and I/O-space names.

Important APIs, types, and functions: Under `ATOM_DEBUG`, it defines `ATOM_OP_NAMES_CNT` with `atom_op_names[]`, `ATOM_TABLE_NAMES_CNT` with `atom_table_names[]`, and `ATOM_IO_NAMES_CNT` with `atom_io_names[]`. Without `ATOM_DEBUG`, all counts are zero and no arrays are emitted.

Control flow: Build-time conditional only. Debug code can index these arrays for readable trace/log output when ATOM interpreter debugging is enabled.

State and persistence: Static string tables are compile-time read-only diagnostic data. No runtime driver state is modified.

Dependencies and integration points: Includes `atom.h` for ATOM opcode/table definitions and is used by Radeon ATOM parser/interpreter debug paths.

Risks: Counts must match array contents and opcode/table numbering. Debug names can become stale if ATOM opcodes or table indices change. Arrays are `char *` rather than `const char *`, which is historically common but less strict.

Test signals: Build with and without `ATOM_DEBUG`; enable ATOM debug traces and verify opcode/table names line up with interpreted BIOS commands; bounds-check any debug indexing against the count macros.
