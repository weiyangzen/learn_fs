# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/atom-names.h

### Purpose
`atom-names.h` supplies optional debug name tables for the AMD ATOM BIOS interpreter. When `ATOM_DEBUG` is enabled, it maps ATOM opcode numbers, command table indexes, and I/O space identifiers to readable strings for debug logs.

### Important APIs, Types, And Functions
Under `#ifdef ATOM_DEBUG`, the header defines `ATOM_OP_NAMES_CNT` as `123` and initializes `atom_op_names[]`, defines `ATOM_TABLE_NAMES_CNT` as `74` and initializes `atom_table_names[]`, and defines `ATOM_IO_NAMES_CNT` as `5` and initializes `atom_io_names[]`. Without `ATOM_DEBUG`, the three count macros are all `0` and no arrays are emitted. The file includes `atom.h` for opcode/table constants but defines no functions or structs.

### Control Flow
There is no runtime control flow in this header, but the compile-time branch changes what debug data exists. In `amdgpu/atom.c`, `ATOM_DEBUG` is defined before including this header, so command execution can print `atom_op_names[op]` when `op < ATOM_OP_NAMES_CNT`. The runtime print path is gated by `amdgpu_atom_debug`, so the arrays are present for debugging but only used when debug output is enabled.

### State, Persistence, And Dependencies
The arrays are static file-local data in each translation unit that includes the header with `ATOM_DEBUG` set. They persist for the lifetime of the module but hold only constant string pointers. The header depends on `atom.h` and on the arrays staying synchronized with the interpreter's opcode numbering and ATOM table indexes.

### Integration Points
The direct integration point is `amdgpu/atom.c`, where the opcode names annotate interpreter traces such as command-table execution offsets. The table and I/O names are available for related ATOM debug output in the same translation unit if used by debug paths.

### Risks
The count values and initializer order must track the opcode and table definitions. If new opcodes are added without updating the table, debug traces can print numeric fallbacks or misleading names. Because the arrays are declared `static char *` rather than `static const char * const`, accidental mutation would be possible inside the translation unit, though current use treats them as read-only debug labels. Including this header with `ATOM_DEBUG` in many C files would duplicate the static arrays.

### Test Signals
Signals include builds with and without `ATOM_DEBUG`, enabling `amdgpu_atom_debug` and confirming opcode traces match executed ATOM bytecode, bounds checks where opcodes at or above `ATOM_OP_NAMES_CNT` print numeric fallbacks, and review checks that opcode/table count constants stay aligned with `atom.h` and the interpreter dispatch table.
