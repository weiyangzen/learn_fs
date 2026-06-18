# sources/distributed-fs/ceph-client/arch/sparc/kernel/kprobes.c

Purpose: Implements SPARC64 kprobes and kretprobes using software single-step emulation because the architecture lacks suitable hardware single-step support.

Important APIs/types/functions: Per-CPU `current_kprobe` and `kprobe_ctlblk` track the active probe, saved `tnpc`, saved PIL bits, and reentry state. `arch_prepare_kprobe()`, `arch_arm_kprobe()`, and `arch_disarm_kprobe()` copy original instructions, install `BREAKPOINT_INSTRUCTION`, and flush I-cache. `kprobe_handler()` runs pre-handlers and redirects execution to `p->ainsn.insn[0]` followed by a second breakpoint. `post_kprobe_handler()`, `resume_execution()`, `relbranch_fixup()`, and `retpc_fixup()` restore control flow after the copied instruction. `kprobe_fault_handler()` handles faults during active probes. `kprobe_trap()` bridges trap levels `0x170` and `0x171` to `notify_die()`. Kretprobe support is in `arch_prepare_kretprobe()`, `trampoline_probe_handler()`, `kretprobe_trampoline_holder()`, and `arch_init_kprobes()`.

Control flow: The first breakpoint disables preemption, resolves the probe, optionally runs `pre_handler`, masks PIL interrupts, and executes the copied instruction in the probe slot. The second breakpoint runs `post_handler`, fixes `tpc`/`tnpc` and return-PC-producing instructions, restores the saved PIL, clears or restores nested probe state, and re-enables preemption. Reentered probes single-step without invoking user handlers and increment missed counts.

State and persistence: State is per-CPU and live only during trap handling, plus permanent probe instruction slots and the registered trampoline kprobe. The code temporarily rewrites kernel text and must keep copied instructions coherent with `flushi()`.

Dependencies and integration points: It integrates Linux kprobes/kretprobes, die notifiers, exception tables, SPARC trap levels, register windows, I-cache flushing, and `__kretprobe_trampoline_handler()`.

Risks and test signals: Relative branch and `call`/`jmpl` fixups are high risk because copied instruction addresses differ from real addresses. Register-window spills during `retpc_fixup()` must be correct for `%i/%l` destinations. Tests should include probes on calls, branches, delay-slot-adjacent code, nested probes, removed probes racing with trap delivery, kretprobes, and faulting probed instructions with exception-table fixups.
