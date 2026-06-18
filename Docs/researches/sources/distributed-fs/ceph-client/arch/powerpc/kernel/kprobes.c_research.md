
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/kprobes.c

Purpose: PowerPC architecture backend for generic kprobes, including symbol lookup quirks, probe instruction preparation, breakpoint arming, trap handling, single-step/emulation, nested probe handling, and fault recovery.

Important APIs/types/functions: per-CPU `current_kprobe` and `kprobe_ctlblk`; `kprobe_lookup_name`; `arch_adjust_kprobe_addr`; `arch_prepare_kprobe`; `arch_arm_kprobe`; `arch_disarm_kprobe`; `arch_remove_kprobe`; `kprobe_handler`; `kprobe_post_handler`; `kprobe_fault_handler`; `arch_trampoline_kprobe`; helpers around `emulate_step`, `enable_single_step`, `patch_instruction`, and `search_exception_tables`.

Control flow: registration rejects unaligned addresses, instructions that cannot single-step, and placement on the second word of prefixed instructions. It allocates an executable instruction slot, copies the original instruction there, and replaces the probed address with `BREAKPOINT_INSTRUCTION` when armed. Trap handling ignores user mode and non-translated non-BookE contexts, disables preemption, locates the probe, runs the pre-handler, then either emulates the instruction through `emulate_step` or redirects NIP to the copied instruction for hardware single-step. The post handler verifies that execution returned from the copied instruction, runs the post-handler, restores NIP/MSR, and releases the per-CPU probe state. Recursive hits save and restore the previous `kprobe_ctlblk` state and count missed probes instead of running user handlers.

State and persistence: state is per-CPU and transient: current probe pointer, saved MSR, previous nested probe fields, and per-probe `ainsn` slot plus `boostable` hint. There is no filesystem persistence, but live kernel text is modified until the probe is disarmed or removed.

Dependencies and integration: integrates generic kprobes, kallsyms, ftrace location lookup, PPC64 ELF ABI v1/v2 entry rules, text patching, PowerPC instruction decoding, software single-step, exception tables, and rethook trampoline support.

Risks: incorrect symbol entry adjustment can probe descriptors rather than code; prefixed instruction handling must prevent half-instruction probes; faults while single-stepping must restore MSR and preemption state exactly; probe recursion suppresses handlers and can hide expected callbacks; self-modifying text requires correct cache synchronization through `patch_instruction`.

Test signals: build with `CONFIG_KPROBES` across PPC32/PPC64 ABI variants, register probes by name and address, probe ftrace entry points, exercise prefixed instruction rejection, trigger nested probes and faulting load/store probes, and verify no stuck preemption or incorrect NIP after post handling.
