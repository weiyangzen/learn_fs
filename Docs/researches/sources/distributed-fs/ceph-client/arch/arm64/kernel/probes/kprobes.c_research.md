# sources/distributed-fs/ceph-client/arch/arm64/kernel/probes/kprobes.c

Purpose: this is the ARM64 backend for kernel kprobes and kretprobes. It allocates executable instruction slots, installs breakpoint instructions into kernel text, manages per-CPU active probe state, handles breakpoint/single-step exceptions, and implements return-probe trampoline handling.

Important APIs and state: per-CPU `current_kprobe` and `kprobe_ctlblk` track active and nested probes. `alloc_insn_page()` allocates ROX kprobe XOL memory. `arch_prepare_kprobe()` validates alignment, excludes exception-table addresses, decodes the instruction, allocates an XOL slot when needed, and prepares either single-step or simulation metadata. `arch_arm_kprobe()` and `arch_disarm_kprobe()` patch text with `BRK64_OPCODE_KPROBES` or the original opcode. Exception handlers include `kprobe_brk_handler()`, `kprobe_ss_brk_handler()`, `kprobe_fault_handler()`, and `kretprobe_brk_handler()`.

Control flow: a probe hit sets the current per-CPU probe, runs the pre-handler if present, then either redirects PC to the XOL slot with DAIF masked or calls the simulator and immediately performs post handling. The XOL slot contains the original instruction followed by an ARM64 kprobe single-step breakpoint. On the single-step breakpoint, the handler restores DAIF, fixes PC to `xol_restore` for non-branching instructions, invokes the post-handler, and clears probe state. Nested hits are allowed only from specific states and otherwise BUG. Faults during XOL execution rewind PC to the original probe address and let normal fault handling proceed.

Dependencies and integration: depends on text patching, debug monitor hooks, exception tables, execmem, per-CPU kprobe core state, and the instruction decoder. `arch_populate_kprobe_blacklist()` blocks entry, irqentry, hyp, and hyp-idmap text ranges. Kretprobes replace LR with `__kretprobe_trampoline`, handled by `kretprobe_brk_handler()`.

Risks: per-CPU state requires interrupts masked while executing XOL to avoid migration/nesting surprises. Text patching and cache maintenance ordering are critical. Reentrancy bugs are fatal. Blacklist gaps could allow probes in code that cannot tolerate breakpoint exceptions.

Test signals: kprobes/kretprobes selftests, blacklist contents in debugfs, probes on simulated and XOL instructions, fault-in-probe tests, and nested probe stress. Bad behavior appears as missed probes, bad PC restore, WARN/BUG in reentry, or crashes in exception entry code.
