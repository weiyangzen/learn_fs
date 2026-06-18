# sources/distributed-fs/ceph-client/arch/riscv/kernel/patch.c

Purpose: Provides safe RISC-V kernel text patching primitives for alternatives, ftrace, jump labels, kprobes, and module code.

Important APIs/types/functions: Defines `patch_text_set_nosync()`, `patch_insn_write()`, `patch_text_nosync()`, `patch_text()`, fixmap mapping helpers, and `riscv_patch_in_stop_machine`.

Control flow: Runtime patching maps target text writable through fixmap when strict kernel RWX is active, writes bytes or instructions, flushes instruction cache, and optionally synchronizes all CPUs with `stop_machine()` for fully synchronized patching.

State and persistence: Mutates executable kernel or module text. Uses fixmap slots and global patching state during operations.

Dependencies and integration points: Depends on `text_mutex`, fixmap, set_memory permissions, cacheflush, stop_machine, alternatives, ftrace, kprobes, and jump labels.

Risks and test signals: Partial instruction writes, missing icache flushes, or patching freed text can crash live CPUs. Test alternatives at boot/module load, kprobe arm/disarm, ftrace toggling, jump label stress, strict RWX, and SMP patching races.
