# sources/distributed-fs/ceph-client/arch/x86/kernel/kprobes/ftrace.c

Purpose: Implements the x86 backend for kprobes-on-ftrace, letting probes at ftrace locations run from the ftrace callback path instead of patching an int3 breakpoint.

Important APIs/types/functions: defines `kprobe_ftrace_handler()` and `arch_prepare_kprobe_ftrace()`. It uses `ftrace_get_regs()`, `ftrace_test_recursion_trylock()`, `get_kprobe()`, per-CPU `current_kprobe`, and `struct kprobe_ctlblk`.

Control flow: the ftrace callback returns immediately when globally disabled or recursion lock acquisition fails. It looks up a kprobe at the ftrace IP and ignores missing or disabled probes. If another kprobe is already running, it increments missed count. Otherwise it sets `regs->ip` to `ip + INT3_INSN_SIZE` to mimic normal int3 entry, records the current probe, runs the pre-handler, optionally emulates a post-handler by advancing to `ip + MCOUNT_INSN_SIZE`, then restores the original IP and clears current-probe state.

State and persistence: no private persistent state. It uses the same registered `struct kprobe` objects and per-CPU kprobe state as core kprobes. `arch_prepare_kprobe_ftrace()` marks the architecture instruction slot as absent and non-boostable.

Dependencies and integration points: depends on dynamic ftrace with register saving, kprobes core, ftrace recursion protection, x86 int3 size and ftrace mcount instruction size conventions, and `common.h` declarations.

Risks: the fake int3 IP convention must match kprobe handlers that expect the breakpoint address plus one. Post-handler emulation assumes a 5-byte ftrace NOP/mcount site. Recursion handling is necessary because ftrace callbacks can run in sensitive contexts with preemption disabled.

Test signals: kprobes-on-ftrace selftests should place probes on ftrace-capable functions, verify pre/post handler register IP values, nested probe missed counts, global disable behavior, and equivalence with int3 probes for handler return semantics.
