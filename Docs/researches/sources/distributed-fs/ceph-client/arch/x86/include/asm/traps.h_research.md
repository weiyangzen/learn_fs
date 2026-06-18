# sources/distributed-fs/ceph-client/arch/x86/include/asm/traps.h

Purpose: declares x86 trap helper entry points and small inline helpers for signal codes and IRQ restoration around trap handling.

Important APIs/types/functions: `sync_regs()`, `fixup_bad_iret()`, `vc_switch_off_ist()`, `ibt_selftest()`, `handle_invalid_op()`, `handle_bug()`, `get_si_code()`, `math_emulate()`, `fault_in_kernel_space()`, `handle_stack_overflow()`, `cond_local_irq_enable()`, and `cond_local_irq_disable()`.

Control flow: trap code calls architecture helpers to synchronize register frames, fix bad IRET frames, switch off IST for #VC, run IBT selftests, emulate legacy math, handle stack overflow, and conditionally restore interrupt state based on saved `X86_EFLAGS_IF`. `get_si_code()` maps debug register condition bits to ptrace/signal trap codes.

State/persistence: no owned persistent state. It operates on `pt_regs`, debug register condition bits, and stack metadata passed by trap handlers.

Dependencies/integration: depends on context tracking, kprobes, debugreg, IDT entry annotations, siginfo constants, and page-fault masks. Integrated with exception entry assembly/C handlers, KASAN/vmap stack handling, signal delivery, and kprobe/BUG handling.

Risks/test signals: interrupt-state restoration and register-frame fixups are correctness-critical for traps returning to user or kernel mode. Test with x86 exception selftests, kprobes, BUG/UD2 handling, bad IRET tests, VMAP stack overflow tests, #VC on encrypted guests, and debug register signal-code checks.
