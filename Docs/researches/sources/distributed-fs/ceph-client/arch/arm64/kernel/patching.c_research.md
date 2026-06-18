# sources/distributed-fs/ceph-client/arch/arm64/kernel/patching.c

Purpose: Provides safe arm64 instruction and executable text patching primitives used by ftrace, alternatives, jump labels, KGDB, BPF/JIT-style code fill, and module relocation.

Important APIs and state: `patch_lock` serializes fixmap writes. APIs include `aarch64_insn_read()`, `aarch64_insn_write()`, `aarch64_insn_write_literal_u64()`, `aarch64_insn_copy()`, `aarch64_insn_set()`, `aarch64_insn_patch_text_nosync()`, and `aarch64_insn_patch_text()`. Helpers map image or vmalloc text through `FIX_TEXT_POKE0`.

Control flow: writes acquire the raw spinlock with IRQs saved, map the target physical page through fixmap, copy or memset the new instruction data with nofault helpers, unmap, and flush instruction cache as needed. Multi-instruction synchronized patching uses `stop_machine_cpuslocked()` so one master CPU applies patches while others wait and execute `isb()`.

Dependencies and integration: depends on fixmap, cache maintenance, stop_machine, kernel nofault access, `core_kernel_text()`, `vmalloc_to_page()`, and executable section symbols including exit text before init discard.

Risks and test signals: risks are patching unaligned A64 instructions, missing cache synchronization, writing freed init/exit text after boot, vmalloc text without pages, and deadlocks under patch_lock. Test with ftrace, alternatives, jump labels, KGDB breakpoints, BPF/JIT fill users, CPU hotplug, and fault injection on nofault copies.
