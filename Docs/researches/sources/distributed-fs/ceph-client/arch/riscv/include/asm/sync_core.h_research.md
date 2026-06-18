<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/sync_core.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/sync_core.h

Purpose: Provides instruction-stream/core synchronization helpers after text modification.

Important APIs/types/functions: Defines `sync_core()` and related architecture hooks using `fence.i`/instruction synchronization.

Control flow: Callers invoke synchronization after code patching so subsequent execution observes modified instructions.

State and persistence: No durable state; effect is hardware ordering of instruction fetch.

Dependencies and integration points: Used by alternatives, ftrace, kprobes, jump labels, BPF JIT, and module patching.

Risks: Missing synchronization can execute stale instructions after patching.

Test signals: Dynamic ftrace, kprobe, jump-label, BPF JIT, module load, and multi-core patching tests.

Source read size: 29 lines, 689 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/sync_core.h -->
