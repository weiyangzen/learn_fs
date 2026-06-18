# sources/distributed-fs/ceph-client/arch/powerpc/kernel/kprobes-ftrace.c

## Purpose
Implements the PowerPC optimized kprobe path that uses ftrace callbacks instead of software breakpoint single-step for eligible probe sites.

## Important APIs, Types, And Functions
Defines `kprobe_ftrace_handler` and `arch_prepare_kprobe_ftrace`. It uses `struct kprobe`, `struct kprobe_ctlblk`, `struct ftrace_ops`, `struct ftrace_regs`, `get_kprobe`, `kprobe_disabled`, `get_kprobe_ctlblk`, `kprobe_running`, `kprobes_inc_nmissed_count`, `current_kprobe`, and `KPROBE_HIT_*` states.

## Control Flow
The ftrace callback returns immediately if kprobe ftrace is globally disabled or recursion lock acquisition fails. It gets `pt_regs`, finds the kprobe for `nip`, skips disabled probes, and either records a missed hit when another kprobe is active or runs the pre-handler. PowerPC adjusts NIP backward before the pre-handler because the ftrace call site reports NIP after the mcount instruction. If the pre-handler does not redirect control, the code emulates a NOP by advancing NIP and optionally calls the post-handler. It then clears `current_kprobe` and releases the ftrace recursion lock.

## State And Persistence
State is per-CPU `current_kprobe` and `kprobe_ctlblk.kprobe_status`, plus per-probe missed-hit counters. `arch_prepare_kprobe_ftrace` marks the optimized instruction slot as unused and boostability as disabled.

## Dependencies And Integration Points
Depends on ftrace with register capture, generic kprobes, PowerPC `regs_add_return_ip`, mcount instruction size, recursion protection, and NOKPROBE marking to avoid probing the handler itself.

## Risks And Edge Cases
Risks include incorrect NIP adjustment, recursion through ftrace/kprobe handlers, pre-handler redirection requiring post-handler suppression, missing probes when `get_kprobe` fails, and interactions with hardirq/preempt context. The handler must not itself be probed.

## Test Signals
Signals include kprobes selftests with ftrace optimization enabled, pre/post handlers that modify NIP, nested probe miss accounting, disabled probe behavior, ftrace recursion stress, and comparison with breakpoint-based kprobe behavior.
