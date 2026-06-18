# sources/distributed-fs/ceph-client/arch/x86/kernel/process_32.c

## Purpose
Implements 32-bit x86-specific register display, thread release, user-mode start frame setup, and task context switching.

## APIs, Types, And Functions
Key functions are `__show_regs()`, `release_thread()`, `start_thread()`, and `__switch_to()`. It exports `start_thread()`.

## Control Flow
`__show_regs()` prints general registers, segment selectors, EFLAGS, and optionally CR/debug registers. `release_thread()` asserts the task has no `mm` and releases vm86 IRQs. `start_thread()` clears GS, initializes user DS/ES/SS/CS, sets IP/SP, and enables interrupts in EFLAGS. `__switch_to()` saves FPU state, saves outgoing GS, loads next TLS, performs extra switch work, ends paravirt lazy mode, updates kernel stack and SYSENTER state, restores GS, writes `current_task`, and schedules Intel resctrl state.

## State And Persistence
Persists user segment and GS state in `thread_struct`, stack-top/TSS state per CPU, and resctrl scheduling state. No standalone storage is introduced.

## Dependencies And Integration
Depends on scheduler switch assembly, FPU context switching, TLS/GDT loading, vm86, paravirt `arch_end_context_switch()`, SYSENTER refresh, `process.h`, and resctrl.

## Risks And Test Signals
Risks include stale segment selectors, bad SYSENTER CS after vm86 transitions, FPU state loss, and incorrect current stack tracking. Test signals include 32-bit userspace boot, vm86 coverage, TLS/threading tests, ptrace register dumps, context-switch stress, and resctrl scheduling tests.
