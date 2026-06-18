# sources/distributed-fs/ceph-client/scripts/gendwarfksyms/examples/symbolptr.c

## Purpose
`examples/symbolptr.c` demonstrates `__gendwarfksyms_ptr_` fallback symbols used when an exported symbol lacks direct DWARF type information.

## Important APIs, Types, and Functions
`__GENDWARFKSYMS_EXPORT(sym)` creates a used pointer variable in `___gendwarfksyms_ptr+sym` with `typeof(sym) *`. The file declares/defines function and pointer symbols `f`, `g`, and `p`.

## Control Flow
There is no runtime flow. The section variables force the compiler to emit pointer type information that `symbols.c` and `dwarf.c` can associate with exports.

## State and Persistence Behavior
Compiled objects contain special section symbols and DWARF pointer types used during version generation.

## Dependencies and Integration Points
It integrates with `SYMBOL_PTR_PREFIX` handling in `gendwarfksyms.h`, `symbols.c`, and `dwarf.c`.

## Risks and Test Signals
The pointer symbol must have the same type as the exported symbol. Test that `gendwarfksyms` can version symbols absent from direct DWARF by using the pointer fallback.
