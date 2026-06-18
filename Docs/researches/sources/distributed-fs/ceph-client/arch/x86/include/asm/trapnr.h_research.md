# sources/distributed-fs/ceph-client/arch/x86/include/asm/trapnr.h

Purpose: defines x86 event-type codes and exception/trap vector numbers.

Important APIs/types/functions: `EVENT_TYPE_*` constants and `X86_TRAP_*` values for divide error, debug, NMI, breakpoint, overflow, invalid opcode, device-not-available, double fault, TSS, segment, general protection, page fault, machine check, SIMD FP, virtualization/control-protection/VC, and IRET exception.

Control flow: none; hardware and virtualization entry/exit code use these constants to classify events.

State/persistence: no state.

Dependencies/integration: used by IDT/FRED, Intel VT-x, AMD SVM, trap handlers, signal delivery, tracing, and exception fixup paths.

Risks/test signals: constants are ABI-like architecture facts; changes would break exception dispatch and virtualization injection. Test through exception selftests, KVM event injection, FRED/legacy IDT builds, debug/breakpoint handling, and page-fault/machine-check smoke tests.
