# sources/distributed-fs/ceph-client/arch/x86/kernel/kprobes/core.c

Purpose: Implements baseline x86 kprobes: deciding whether an address can be probed, copying and relocating the probed instruction, patching int3 breakpoints into kernel text, handling int3 traps, emulating control-flow-sensitive instructions, and restoring execution after out-of-line single stepping.

Important APIs/types/functions: defines per-CPU `current_kprobe` and `kprobe_ctlblk`, `kretprobe_blacklist`, `can_boost()`, `recover_probed_instruction()`, `arch_adjust_kprobe_addr()`, `__copy_instruction()`, `arch_prepare_kprobe()`, `arch_arm_kprobe()`, `arch_disarm_kprobe()`, `arch_remove_kprobe()`, `kprobe_int3_handler()`, `kprobe_fault_handler()`, and blacklist/init hooks. Helper families handle relative instruction synthesis, instruction-boundary validation, emulation, single-step setup/resume, and reentry.

Control flow: registration rejects alternative-text ranges, validates the target is an instruction boundary inside a symbol, skips exception/CFI-sensitive instructions, allocates an executable instruction slot, copies the original instruction, adjusts RIP-relative displacement, chooses emulation or out-of-line stepping, and stores the original first byte. Arming patches one byte of int3 into text and reports a perf text-poke event. Trap handling ignores user mode, looks up a kprobe at `ip - 1`, runs the pre-handler, either emulates or redirects IP to copied instruction, then catches the second int3 from the slot to resume original IP and invoke the post-handler.

State and persistence: state persists in registered `struct kprobe` objects, executable instruction slots, patched kernel text, and per-CPU current-probe control blocks. Boostable probes add a relative jump in the copied instruction slot when preemption is off and no post-handler is needed.

Dependencies and integration points: depends on kprobes core, x86 instruction decoder, kallsyms, exception tables, CFI trap metadata, ftrace and optprobe instruction recovery, KGDB breakpoint detection, text-poking, perf text-poke events, objtool no-probe annotations, and executable-memory slot allocators.

Risks: instruction decoding and RIP-relative displacement relocation are correctness-critical. Probing exception-fixup, CFI decode, alternative, ftrace, or KGDB-modified code can corrupt execution and is explicitly guarded. Reentered probes skip user handlers and can BUG on unrecoverable nested states. Faults during copied instruction execution must reset IP back to the original address.

Test signals: kprobe selftests should cover normal pre/post handlers, handler-modified IP, ret/call/jmp/jcc/loop/IF-emulated instructions, RIP-relative instructions, nested probes, optprobe recovery interaction, KGDB conflict, faulting copied instructions, blacklist coverage for entry text, and arm/disarm text-poke events.
