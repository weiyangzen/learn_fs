<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/extable.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/extable.h

## Purpose
This header defines SPARC exception-table entry handling.

## Important APIs, Types, and Functions
It describes exception-table entry layout and fixup address extraction for fault recovery.

## Control Flow
Fault handlers search exception tables and redirect execution to fixup code when a faulting instruction is recoverable.

## State and Persistence Behavior
Exception tables are compiled metadata. Runtime state changes only through adjusted instruction pointers during faults.

## Dependencies and Integration Points
It integrates with user access, copy routines, module exception tables, and generic extable search.

## Risks
Incorrect relative address decoding or sorting breaks recoverable fault handling and can turn user-copy faults into kernel oopses.

## Test Signals
Run usercopy fault tests, module exception table tests, and fault injection around copy_from/to_user.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/extable.h -->
