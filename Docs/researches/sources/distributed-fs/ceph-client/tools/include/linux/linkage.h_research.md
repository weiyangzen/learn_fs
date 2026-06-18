<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/linkage.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/linkage.h

## Purpose
`linkage.h` gives tools assembly code a minimal subset of kernel symbol annotation macros.

## APIs And Flow
It includes `linux/export.h` and defines `SYM_FUNC_START`, `SYM_FUNC_END`, `SYM_DATA_START`, `SYM_DATA_START_LOCAL`, and `SYM_DATA_END`. Start macros emit `.globl` and a label; end macros are empty.

## State, Dependencies, Risks, Tests
There is no runtime state. Integration is with assembler sources imported from the kernel that expect modern `SYM_*` annotations. Risks are missing ELF type, size, alignment, and CFI metadata compared with the kernel macros, which can affect tooling but not simple labels. Test signals are assembling tools objects and checking exported symbols with `nm` or `readelf`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/linkage.h -->
