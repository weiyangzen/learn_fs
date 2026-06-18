<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sighandling.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/sighandling.h

Purpose: declares x86 signal handling entry points and helpers. Important APIs include `do_signal()`, `do_notify_resume()`, signal setup/restore helpers, and architecture-specific fault-to-signal glue declarations.

Control flow: return-to-user paths call notification/signal handling when thread flags request work; signal setup builds frames and modifies `pt_regs`, while sigreturn validates and restores user state. State is task signal state plus transient user frames.

Dependencies include `pt_regs`, generic signal code, thread flags, FPU restore, and syscall restart machinery. Risks include incorrect restart state, missed user-return work, or unsafe register restoration. Test signals include signal stress, syscall restart, ptrace-signal interactions, compat signals, and return-to-user work flag tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/sighandling.h -->
