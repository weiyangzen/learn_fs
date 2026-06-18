<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/ucontext.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/ucontext.h

Purpose: Defines PowerPC user context structures for signal handling and context APIs.

Important APIs/types/functions: 32-bit `struct mcontext` and cross-ABI `struct ucontext` with flags, link, stack, signal mask growth padding, and machine context.

Control flow: Signal delivery and `getcontext`/`setcontext`-style libc code use this structure to save and restore execution context.

State and persistence: User context persists in signal frames or userspace-managed context objects.

Dependencies and integration points: Depends on sigcontext/elf and signal headers. Integrated by signal code, libc, and debuggers.

Risks: ppc64 and ppc32 layouts differ and are ABI-sensitive. Signal mask expansion padding is intentional for glibc compatibility.

Test signals: ucontext/signal tests, FP/VMX context preservation, altstack tests, and libc ABI checks.

Source read size: 41 lines, 975 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/ucontext.h -->
