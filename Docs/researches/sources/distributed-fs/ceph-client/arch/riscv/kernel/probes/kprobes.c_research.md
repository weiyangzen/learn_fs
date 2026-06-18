# sources/distributed-fs/ceph-client/arch/riscv/kernel/probes/kprobes.c

Purpose: Implements RISC-V kprobe arming, trap handling, single-step/simulation, reentry, fault recovery, and blacklist setup.

Important APIs/types/functions: Defines per-CPU `current_kprobe` and `kprobe_ctlblk`, `arch_prepare_kprobe()`, `arch_arm_kprobe()`, `arch_disarm_kprobe()`, `arch_remove_kprobe()`, `kprobe_breakpoint_handler()`, `kprobe_single_step_handler()`, `kprobe_fault_handler()`, `arch_populate_kprobe_blacklist()`, `arch_trampoline_kprobe()`, and `arch_init_kprobes()`.

Control flow: Preparation validates addresses, decodes instruction length/type, and either builds an out-of-line single-step slot or marks the instruction for simulation. Arming patches a breakpoint into text. Breakpoint traps find the kprobe, run pre-handlers, set up single-step or simulation, and later post-handlers restore state. Fault handling rewinds PC or restores nested probe state, while reentry logic tracks missed probes and nested status.

State and persistence: Per-CPU current probe and control block track active/reentered probes, saved IRQ flags, previous probes, and status. Probe slots and patched text persist while probes are armed.

Dependencies and integration points: Depends on text patching, extable, RISC-V break instruction encoding, instruction decoder/simulator, trap handling, irqentry blacklist symbols, and generic kprobes/rethook.

Risks and test signals: Probe reentry, compressed instruction length, PC restoration, and IRQ flag restoration are delicate. Test kprobes on kernel text and modules, kretprobes, nested probes, probes in exception paths rejection, faulting probed instructions, and concurrent arm/disarm.
