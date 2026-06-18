<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/objtool_types.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/objtool_types.h

## Purpose
`objtool_types.h` defines unwind and annotation constants shared with objtool-aware assembly and metadata consumers.

## APIs And Flow
It declares `struct unwind_hint` for non-assembly builds, with fields for instruction pointer, stack offset, stack register, unwind type, and signal flag. It defines `UNWIND_HINT_TYPE_*`, `ANNOTYPE_*`, and `ANNOTYPE_DATA_SPECIAL`. There is no control flow; these values describe metadata.

## State, Dependencies, Risks, Tests
State persists in generated object metadata or inline assembly annotations. It depends on `linux/types.h` outside assembly. Risks are ABI drift with objtool and ORC unwinder expectations, incorrect packed layout assumptions, and assembly/C disagreement over numeric constants. Tests should compare structure size and constant values with kernel headers and run objtool over representative annotated objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/objtool_types.h -->
