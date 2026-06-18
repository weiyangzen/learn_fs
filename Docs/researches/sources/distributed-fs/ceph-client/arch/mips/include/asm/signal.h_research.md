<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/signal.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/signal.h

Purpose: Provides MIPS kernel-side signal helpers and declarations on top of the UAPI signal definitions.

Important APIs/types/functions: Includes `<uapi/asm/signal.h>`, declares `mips_abi_32`, defines `sig_uses_siginfo(ka, abi)` with different behavior for `CONFIG_TRAD_SIGNALS`, includes signal context/info headers, declares `__ARCH_HAS_IRIX_SIGACTION`, protected FP context helpers, and `do_notify_resume`.

Control flow: Signal-delivery paths use `sig_uses_siginfo` to choose old-style versus `siginfo` frames, call protected FP save/restore helpers around user copies, and invoke `do_notify_resume` when returning to user mode with pending work.

State and persistence: The header coordinates per-task ABI and signal-frame state, but stores no data itself. The declarations interact with user signal frames, FP context, and thread-info flags.

Dependencies and integration points: Depends on UAPI signal constants, MIPS ABI structures, `asm/sigcontext.h`, `asm/siginfo.h`, and signal implementation files under `arch/mips/kernel`.

Risks: Signal-frame selection is ABI-sensitive, especially with traditional IRIX-style signals and O32 compat. Protected FP context helpers must handle user access failures without corrupting saved state.

Test signals: Signal ABI tests across O32/N32/N64, siginfo versus old signal handlers, FP context preservation tests, and kernel return-to-user tests are relevant.

Source read size: 36 lines, 1126 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/signal.h -->
