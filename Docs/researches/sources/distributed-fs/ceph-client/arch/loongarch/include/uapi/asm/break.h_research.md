<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/break.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/break.h

Purpose: defines LoongArch `break` instruction immediate values reserved for kernel/user debug semantics.
Important APIs and types: constants include `BRK_DEFAULT`, `BRK_BUG`, `BRK_KDB`, user breakpoint and single-step IDs, arithmetic trap IDs, kprobe, and uprobe break values.
Control flow: exception handlers decode break immediates and route to BUG, KGDB, kprobe, uprobe, debugger, or fault handling.
State and persistence: constants are part of userspace/debugger ABI for break instruction interpretation.
Dependencies and integration: used by KGDB, kprobes, uprobes, BUG handling, ptrace/debuggers, and instruction generation.
Risks and test signals: value collisions route traps to the wrong subsystem. Signals include kprobe/uprobe/KGDB tests, BUG traps, and debugger breakpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/uapi/asm/break.h -->
