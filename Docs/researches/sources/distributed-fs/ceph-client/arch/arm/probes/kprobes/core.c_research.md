<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/core.c -->
# sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/core.c

Purpose: implements ARM architecture kprobe and kretprobe lifecycle: instruction preparation, breakpoint patching, trap dispatch, single-step simulation/emulation, fault recovery, return-probe trampoline setup, undefined-instruction hook registration, and blacklist checks.

Important functions: `arch_prepare_kprobe()`, `arch_arm_kprobe()`, `arch_disarm_kprobe()`, `arch_remove_kprobe()`, `kprobes_remove_breakpoint()`, `kprobe_handler()`, `kprobe_trap_handler()`, `kprobe_fault_handler()`, `__kretprobe_trampoline()`, `arch_prepare_kretprobe()`, `arch_init_kprobes()`, and `arch_within_kprobe_blacklist()`. Per-CPU state is `current_kprobe` and `kprobe_ctlblk`.

Control flow: probe registration decodes the target instruction according to ARM/T16/T32 mode, allocates an instruction slot when needed, flushes caches, and rejects unsupported or stack-unsafe instructions. Arming patches an undefined-instruction breakpoint with ISA-appropriate encoding. Trap handling looks up the probe at PC, checks conditional execution, handles recursive hits, runs pre-handler, single-steps via the selected `ainsn` function, runs post-handler, and resets current state. Fault handling restores PC to the original probe address when emulation faults.

State and persistence: modifies kernel text via `patch_text()`/`__patch_text()`, stores prepared instruction slots in `p->ainsn`, and maintains per-CPU current-probe status. Kretprobes replace LR with `__kretprobe_trampoline` and store original return/fp in the instance.

Dependencies and integration: depends on decode/action/checker tables, undefined instruction hooks, text patching, stop_machine synchronization, instruction slot allocators, kprobe core APIs, and ARM exception sections.

Risks: breakpoint removal needs stop_machine to avoid SMP races and Thumb32 halfword tearing. IRQs remain disabled during probe handling to prevent unsupported nesting. Incorrect condition/IT skipping or PC restoration can replay or skip target instructions.

Test signals: `test-core.c` API tests verify kprobe/kretprobe registration, handler calls, unregister behavior, instruction simulation comparisons, and benchmarks. Blacklist behavior is not directly covered by the listed tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/probes/kprobes/core.c -->
