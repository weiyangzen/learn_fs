# sources/distributed-fs/ceph-client/arch/x86/kernel/traps.c

## Purpose
`traps.c` is the central x86 synchronous exception handler implementation. It decodes BUG/WARN trap encodings, routes architectural exceptions to signals or oops paths, handles debug/breakpoint traps, coordinates virtualization/fault special cases, and initializes trap entry infrastructure.

## Important APIs, Types, And Functions
Visible functions include `is_valid_bugaddr()`, `decode_bug()`, `__warn_args()`, `handle_bug()`, `sync_regs()`, `vc_switch_off_ist()`, `fixup_bad_iret()`, many `DEFINE_IDTENTRY*` handlers, and `trap_init()`. Major helpers include `do_trap_no_signal()`, `do_trap()`, `do_error_trap()`, `get_kernel_gp_address()`, `fixup_iopl_exception()`, `try_fixup_enqcmd_gp()`, `gp_try_fixup_and_notify()`, `do_int3()`, `debug_read_reset_dr6()`, `exc_debug_kernel()`, `exc_debug_user()`, `math_error()`, `handle_xfd_event()`, and `ve_raise_fault()`.

## Control Flow
Common trap handling tries vm86, exception-table, vDSO, kprobe, notifier, or feature-specific fixups before recording trap state and signaling or dying. Invalid-op handles BUG/WARN/UBSAN/CFI trap encodings before full exception entry. #GP handles ENQCMD PASID activation, vm86, IOPL CLI/STI emulation, UMIP/vsyscall/vDSO fixups, user SIGSEGV, and kernel address hints. #DB splits user and kernel paths, resets DR6 early, disables local breakpoints for kernel handling, and sends SIGTRAP for user events. #DF handles espfix and stack-overflow cases before panic.

## State, Persistence, Dependencies, Integration
State includes `thread.error_code`, `trap_nr`, `cr2`, `virtual_dr6`, DR6/DR7/debugctl, PASID activation, XFD MSRs, FPU/xstate, IDT/FRED setup, and exception stacks. Dependencies include entry code, notifiers, kprobes/kgdb, BUG/UBSAN/CFI reporting, FPU, TDX/SEV-ES, UMIP, vsyscall, vm86, MCE/NMI discipline, and text patching. Signal files expose saved trap state; `step.c` and `static_call.c` interact with #DB and trap encodings.

## Risks And Test Signals
Privilege-boundary noinstr paths require exact IRQ/RCU/instrumentation state. BUG decoding reads kernel text. #VE cannot occur in syscall gaps or early NMI entry safely. #DB recursion depends on DR7 save/restore. Test divide/overflow/UD/BUG/WARN/UBSAN/CFI, #BP with kprobes/kgdb/text poking, ptrace #DB, vm86, bad IRET, espfix #DF, stack guard overflow, ENQCMD PASID #GP, UMIP/vsyscall/vDSO, FPU/SIMD, XFD, TDX #VE, SEV-ES #VC, and FRED vs IDT.
