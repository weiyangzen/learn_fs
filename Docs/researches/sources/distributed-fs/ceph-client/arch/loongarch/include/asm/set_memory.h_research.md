<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/set_memory.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/set_memory.h

Purpose: declares architecture hooks for changing kernel linear/text mapping attributes.
Important APIs and types: declares `set_memory_x`, `set_memory_nx`, `set_memory_ro`, `set_memory_rw`, and `set_memory_rox` style helpers depending on config.
Control flow: callers such as instruction patching switch pages writable, copy code, then restore executable/read-only permissions.
State and persistence: changes persist in kernel page tables and require cache/TLB coherency handled by implementation files.
Dependencies and integration: integrates with generic `set_memory` APIs, module loading, ftrace/static-call patching, and `inst.c` text modification.
Risks and test signals: wrong permissions can leave text writable or non-executable. Signals include module load/unload, ftrace, live patching, strict RWX checks, and boot warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/set_memory.h -->
