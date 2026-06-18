# sources/distributed-fs/ceph-client/arch/parisc/kernel/kprobes.c

## Purpose

`kprobes.c` implements PA-RISC kprobes and kretprobes. It patches probe sites with break instructions, executes copied instructions from slots, handles single-step completion, manages reentrant probes, and installs a kretprobe trampoline.

## Important APIs, Types, And Functions

Per-CPU state is `current_kprobe` and `kprobe_ctlblk`. Probe lifecycle hooks are `arch_prepare_kprobe()`, `arch_remove_kprobe()`, `arch_arm_kprobe()`, and `arch_disarm_kprobe()`. Runtime handlers are `parisc_kprobe_break_handler()` and `parisc_kprobe_ss_handler()`.

Reentry helpers include `save_previous_kprobe()`, `restore_previous_kprobe()`, `set_current_kprobe()`, and `setup_singlestep()`. Kretprobe support is provided by `__kretprobe_trampoline()`, `trampoline_probe_handler()`, `arch_kretprobe_fixup_return()`, `arch_prepare_kretprobe()`, `arch_trampoline_kprobe()`, and `arch_init_kprobes()`.

## Control Flow

Preparing a kprobe rejects unaligned addresses, allocates an instruction slot, saves the original opcode, copies it into slot word 0, places `PARISC_KPROBES_BREAK_INSN2` in slot word 1, and flushes the slot. Arming patches the original address with `PARISC_KPROBES_BREAK_INSN`; disarming restores the original opcode.

On the first break, `parisc_kprobe_break_handler()` disables preemption, looks up a kprobe at `iaoq[0]`, handles reentry by saving prior state and single-stepping without user handlers, or sets the current probe and runs the pre-handler. If the pre-handler returns zero or is absent, it redirects execution to the copied instruction slot and marks single-step status; otherwise it clears state and re-enables preemption.

On the second break from the instruction slot, `parisc_kprobe_ss_handler()` verifies the PC is the slot's second instruction, restores previous state for reentry, runs post-handler if present, then reconstructs `iaoq` for branch or non-branch instructions before clearing current kprobe.

For return probes, `arch_prepare_kretprobe()` saves the original return address from `gr[2]` and replaces it with the trampoline address. The trampoline kprobe handler calls the generic kretprobe trampoline handler and consumes the probe.

## State And Persistence Behavior

Runtime state includes patched text, allocated instruction slots, per-CPU kprobe control blocks, saved `iaoq` values, missed-count increments, and modified return addresses for kretprobes. No persistent storage is used.

## Dependencies And Integration Points

The file depends on generic kprobes, text patching, instruction-slot allocation, cache flushing, PA-RISC break instruction constants, function descriptor dereferencing for the trampoline, and `pt_regs` instruction queues.

## Risks

Branch queue reconstruction is subtle; absolute branch instructions use the already computed back queue, while other instructions need sequential queue restoration. Preemption must remain disabled across active probe handling. Reentrant probes intentionally skip user handlers and increment missed counts. Incorrect trampoline descriptor handling would break kretprobes on 64-bit.

## Test Signals

Signals include installing/removing kprobes on aligned function instructions, rejecting unaligned addresses, pre/post handlers receiving correct regs, kretprobes reporting returns, nested probe missed counts increasing, and successful probes on branch and non-branch instructions.
