<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/segment.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/segment.h

Purpose: defines x86 segment selector constants, GDT/LDT entry numbers, descriptor privilege levels, user/kernel code/data selectors, TLS slots, per-CPU segment behavior, and helpers for segment arithmetic. It is a fundamental ABI header for entry, ptrace, TLS, compat, and boot code.

Important APIs/macros: GDT entry identifiers, `__KERNEL_CS`, `__KERNEL_DS`, `__USER_CS`, `__USER_DS`, compat selectors, TLS selector helpers, `SEGMENT_RPL_MASK`, `USER_RPL`, and configuration-specific selectors for 32-bit, 64-bit, SYSENTER/SYSCALL, percpu, and FRED-sensitive paths.

Control flow: entry code, task setup, ptrace, TLS setup, and syscall paths load or compare selectors using these constants. Compat and paravirt paths can use alternate user 64-bit selectors. State is primarily CPU descriptor tables and task TLS descriptors declared elsewhere.

Dependencies include UAPI segment definitions, descriptor tables, LDT/TLS code, entry assembly, and syscall ABI. Risks are extremely high because selector values are hard ABI with assembly, userspace signal/ptrace expectations, and CPU privilege checks. Test signals include native and compat syscall entry/exit, TLS set/get, signal return, ptrace segment access, FRED/non-FRED builds, and boot descriptor-table validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/segment.h -->
