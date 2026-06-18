<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cobalt/mach-gt64120.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cobalt/mach-gt64120.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cobalt/mach-gt64120.h` provides machine-specific constants and declarations for `mach-cobalt`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 2 macros including `_COBALT_MACH_GT64120_H`, `GT64120_BASE`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `GT64120_BASE (1)`, `_COBALT (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is MIPS platform setup, generic architecture headers, board files, and device drivers that include this machine directory.

## Risks
the file is small but part of the architecture ABI; stale constants can fail only on the affected board family.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-cobalt/mach-gt64120.h -->
