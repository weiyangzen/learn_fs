# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kprobes.h

Purpose: Defines PowerPC kprobes and optimized kprobes architecture data structures, instruction slot sizing, handlers, and trampoline symbols.

Important APIs, types, and functions: Defines `kprobe_opcode_t`, optprobe template symbols, instruction size constants, `flush_insn_slot()`, `kretprobe_blacklist_size`, `__kretprobe_trampoline()`, `arch_remove_kprobe()`, `struct arch_specific_insn`, `struct prev_kprobe`, `struct kprobe_ctlblk`, `struct arch_optimized_insn`, and handler prototypes/stubs.

Control flow: Kprobes copies/analyzes the target instruction, installs a breakpoint, emulates or single-steps as needed, tracks nested probes in per-CPU control blocks, and optimized probes patch a branch to an out-of-line template.

State and persistence: Probe state lives in kprobe structs, per-CPU control blocks, instruction slots, and patched kernel text. No disk persistence.

Dependencies and integration points: Depends on generic kprobes, PowerPC instruction analysis, text patching, modules, ptrace regs, and optprobe assembly templates.

Risks: PowerPC instruction emulation and prefixed instruction handling must be correct. Optimized probe branch length is only one instruction. Probes must not recurse into unsafe handlers and text patching must synchronize I-cache.

Test signals: Basic kprobe/kretprobe hits, nested probes, fault handling, optimized probe enable/disable, module probes, blacklist behavior, and prefixed-instruction targets where supported.
