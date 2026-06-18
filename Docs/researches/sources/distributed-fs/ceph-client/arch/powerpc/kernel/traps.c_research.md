# sources/distributed-fs/ceph-client/arch/powerpc/kernel/traps.c

## Purpose
Implements the architecture-specific exception and trap handlers for PowerPC. It turns low-level interrupt vectors into kernel oops/panic paths, debugger/kprobe/uprobe notifications, user signals, instruction emulation, machine-check recovery, facility-unavailable handling, performance/debug exceptions, and optional emulated-instruction accounting.

## Important APIs, Types, And Functions
The externally visible and interrupt-entry functions include `die_will_crash`, `panic_flush_kmsg_start`, `panic_flush_kmsg_end`, `die`, `user_single_step_report`, `_exception`, `_exception_pkey`, `hv_nmi_check_nonrecoverable`, `system_reset_exception`, `machine_check_*`, `die_mce`, `machine_check_exception`, `handle_hmi_exception`, `instruction_breakpoint_exception`, `single_step_exception`, `emulate_single_step`, `program_check_exception`, `emulation_assist_interrupt`, `alignment_exception`, `facility_unavailable_exception`, TM unavailable handlers, `performance_monitor_exception*`, `DebugException`, `altivec_assist_exception`, SPE handlers, `unrecoverable_exception`, `WatchdogException`, and `kernel_bad_stack`. Support helpers include `oops_begin`, `oops_end`, `exception_common`, `show_signal_msg`, `check_io_access`, `parse_fpe`, `emulate_instruction`, string/popcntb/isel emulators, and optional `ppc_emulated` debugfs state.

## Control Flow
Fatal kernel exceptions enter `die()`, optionally give the debugger first chance, serialize oops output with `die_lock`, print machine/MMU/config context, notify die notifiers, dump registers/modules, then trigger fadump/kdump/panic or kill the current task. User exceptions pass through `exception_common`, set `current->thread.trap_nr`, optionally log rate-limited instruction context, and call `force_sig_fault` or `force_sig_pkuerr`. System reset is an NMI path: it preserves HSRRs in HV mode, marks nonrecoverable HSRR scratch windows, lets platform/debugger handlers run, then routes to fadump, kdump, secondary crash holding, oops, and finally `nmi_panic`. Machine checks call platform or CPU handlers, debugger fault handlers, I/O extable recovery, and otherwise `die_mce`.

Program checks decode reason bits for FP exceptions, traps, TM bad-thing exceptions, illegal or privileged instructions, optional math emulation, and user instruction emulation. Successful emulation advances NIP and replays single-step state. Alignment traps try `fix_alignment` unless the task requested `PR_UNALIGN_SIGBUS`. Facility-unavailable traps either lazily enable or emulate DSCR/TM access or signal `SIGILL`. Debug and performance handlers integrate with perf, kprobes, hardware breakpoints, and debugger callbacks.

## State And Persistence
Persistent state is kernel runtime state: debugger callback pointers, oops serialization counters, `current->thread` trap/debug/FP/vector/TM fields, PACA NMI/HMI flags, irq statistics, taint flags, and optional debugfs counters under `emulated_instructions`. No filesystem data is persisted except debugfs-visible counters and console/kmsg output.

## Dependencies And Integration Points
Depends on PowerPC interrupt macros, `pt_regs`, PACA, machine descriptor callbacks, fadump/kexec crash paths, perf, kprobes, bug tables, exception tables, signal delivery, FP/Altivec/VSX/SPE/TM save-restore code, debug registers, cache/TLB platform machine-check handlers, and `udbg` for early machine checks. It is central to user ABI signal behavior and to crash dump reliability.

## Risks And Edge Cases
This file is high risk because many paths run with interrupts disabled, in NMI context, or after register state is partially unrecoverable. HSRR/HSPRG1 NMI windows, machine-check recoverability, real-mode address fixups, TM transaction abort semantics, endian-sensitive vector emulation, prefixed instruction lengths, and single-step replay are correctness-sensitive. Debugger and notifier callbacks can suppress normal signal/oops handling, so ordering matters.

## Test Signals
Useful signals include PowerPC boot and exception selftests, kprobes/uprobes/perf tests, unaligned access tests, ptrace single-step tests, user `SIGILL`/`SIGTRAP` behavior, math/Altivec/SPE emulation tests, kdump/fadump system-reset drills, machine-check injection where available, and cross-builds for Book3S, BookE, 32-bit, 64-bit, TM, VSX, SPE, and advanced debug configurations.
