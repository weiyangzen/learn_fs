# Group Research: group_1190_netbsd_src_sources_os_bsd_netbsd_src_lib_libc_compat_arch_m68k_sys__48a0661f73be

Scope verified against `Docs/research_subset_a.md`: these files are within `sources/os/bsd/netbsd-src`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat___sigtramp1.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat___sigtramp1.S

Implements the m68k legacy `__sigtramp_sigcontext_1` signal trampoline. The kernel calls the signal handler directly; this trampoline runs only after handler return to invoke old-style signal return.

It computes the `sigcontext` pointer from the stack at `12(%sp)`, places it in the argument slot, uses `trap #3` as the special sigreturn trap, and falls back to `exit` with the returned errno if sigreturn fails.

Filesystem relevance is indirect: this is libc ABI compatibility infrastructure, preserving old NetBSD/m68k binaries that may include filesystem-using programs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat___sigtramp1.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat_msgctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat_msgctl.S

Defines the m68k compatibility `msgctl` entry point. It emits a link-time warning telling callers to include `<sys/msg.h>` for the correct modern reference.

The actual implementation is a `PSEUDO(msgctl, compat_14_msgctl)` syscall veneer, routing old `msgctl` references to the NetBSD 1.4 compatibility syscall.

No filesystem logic is present; this is System V IPC ABI compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat_msgctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat_quotactl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat_quotactl.S

Defines the m68k compatibility `quotactl` symbol. It warns that old references should include `<sys/quota.h>` to bind to the correct interface.

The wrapper maps `quotactl` to `compat_50_quotactl`, preserving the pre-NetBSD 5.0 quota-control ABI.

Filesystem relevance is direct: quota control is a filesystem administration syscall, and this file keeps old m68k quota tools ABI-compatible.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat_quotactl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat_shmctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat_shmctl.S

Defines the m68k compatibility `shmctl` entry point. It emits a warning directing users to include `<sys/shm.h>` for the correct modern declaration.

The syscall veneer maps `shmctl` to `compat_14_shmctl`.

This is shared-memory ABI compatibility, not filesystem code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat_shmctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat_sigaction.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat_sigaction.S

Defines m68k compatibility `sigaction`. The file warns old references to include `<signal.h>` for correct symbol selection.

It uses `PSEUDO(sigaction, compat_13_sigaction13)`, preserving the NetBSD 1.3 signal-action ABI.

Filesystem relevance is indirect: signal handling affects all old binaries, including filesystem utilities.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat_sigaction.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat_sigpending.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat_sigpending.S

Implements m68k compatibility `sigpending` around `compat_13_sigpending13`. It includes old SCCS/RCS metadata and emits a warning for direct compatibility references.

After `_SYSCALL`, it stores the returned old integer signal mask through the caller-provided pointer at `4(%sp)`, clears `%d0`, and returns success.

This adapts the legacy integer-mask syscall result to the libc pointer-return API expected by old callers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat_sigpending.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat_sigprocmask.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat_sigprocmask.S

Implements m68k compatibility `sigprocmask` for the NetBSD 1.3 signal-mask ABI. It warns about compatibility references.

If the new mask pointer is null, it changes the operation to `SIG_BLOCK` with an empty mask; otherwise it dereferences the pointed-to old mask and passes the integer mask to `compat_13_sigprocmask13`.

On success it stores the returned old mask through the optional old-mask pointer, then returns zero.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat_sigprocmask.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat_sigreturn.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat_sigreturn.S

Implements m68k legacy `sigreturn`. It warns for compatibility references and notes that register state must be preserved.

The body uses `trap #1`, which is reserved on m68k for `compat_13_sigreturn13`, then branches to `CERROR` if control returns.

The file also adjusts profiling prologue behavior under `GPROF` so sigreturn does not corrupt user register state.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat_sigreturn.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat_sigsuspend.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat_sigsuspend.S

Implements m68k compatibility `sigsuspend` for old integer signal sets. It emits the standard compatibility warning.

The wrapper dereferences the caller’s mask pointer into the syscall argument slot, invokes `compat_13_sigsuspend13`, and normally reports errors through `CERROR`; a successful return is marked as unexpected and returns zero.

This bridges modern pointer-style libc arguments to the legacy mask syscall ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/m68k/sys/compat_sigsuspend.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/Makefile.inc

Build include fragment for MIPS libc compatibility code.

It includes the architecture-specific `gen/Makefile.inc` and `sys/Makefile.inc` fragments through `${COMPATARCHDIR}`.

No source behavior is defined here; it only wires MIPS compatibility objects into the libc build.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/Makefile.inc

Lists MIPS compatibility syscall assembly sources for libc.

The source list includes legacy `vfork`, `__semctl`, signal return/trampoline, SysV IPC controls, signal-mask wrappers, and `quotactl`.

This file is build metadata only.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat_Ovfork.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat_Ovfork.S

Implements MIPS legacy `vfork`. It invokes the `vfork` syscall and uses the MIPS convention where `v1` distinguishes parent from child.

On success, child returns zero while parent returns the child pid in `v0`; on error it tail-calls `__cerror`.

This is process-control ABI compatibility, used by old binaries including filesystem tools.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat_Ovfork.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat___semctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat___semctl.S

Defines the MIPS compatibility `__semctl` syscall veneer.

It includes optional RCS metadata and maps `__semctl` to `compat_14___semctl` via `PSEUDO`.

This is System V semaphore ABI compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat___semctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat___sigreturn14.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat___sigreturn14.S

Defines MIPS `__sigreturn14` as a compatibility wrapper to `compat_16___sigreturn14`.

The file emphasizes preserving user register state during signal return and uses the `PSEUDO` syscall macro.

This supports old signal trampoline paths and legacy binaries.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat___sigreturn14.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat___sigtramp1.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat___sigtramp1.S

Implements MIPS `__sigtramp_sigcontext_1`.

The kernel calls the handler directly; the trampoline takes the `sigcontext` at `sp`, passes it to `compat_16___sigreturn14`, and exits with errno if sigreturn fails.

This is architecture-specific legacy signal ABI support.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat___sigtramp1.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat_msgctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat_msgctl.S

Defines MIPS compatibility `msgctl`.

It emits a compatibility warning and maps `msgctl` to `compat_14_msgctl`.

No filesystem logic is present.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat_msgctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat_quotactl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat_quotactl.S

Defines MIPS compatibility `quotactl`.

It warns that `<sys/quota.h>` should be included and maps the public symbol to `compat_50_quotactl`.

Filesystem relevance is direct because `quotactl` manages filesystem quotas.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat_quotactl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat_shmctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat_shmctl.S

Defines MIPS compatibility `shmctl`.

It warns callers to include `<sys/shm.h>` and routes to `compat_14_shmctl`.

This is shared-memory compatibility glue.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat_shmctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat_sigaction.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat_sigaction.S

Defines MIPS compatibility `sigaction`.

It emits a compatibility warning and maps to `compat_13_sigaction13`.

This preserves old signal action struct/layout ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat_sigaction.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat_sigpending.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat_sigpending.S

Implements MIPS compatibility `sigpending`.

After invoking `compat_13_sigpending13`, it stores the returned mask using `INT_S` at `_SC_ONSTACK(a0)` and returns zero. The use of `assym.h` supplies the sigcontext offset constant.

This is a legacy signal-mask adapter with architecture-specific storage semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat_sigpending.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat_sigprocmask.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat_sigprocmask.S

Implements MIPS compatibility `sigprocmask`.

It converts the pointer argument to the old integer mask when non-null, substitutes `SIG_BLOCK` when null, calls `compat_13_sigprocmask13`, and stores the returned old mask through the optional output pointer.

Errors tail-call `__cerror`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat_sigprocmask.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat_sigreturn.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat_sigreturn.S

Defines MIPS compatibility `sigreturn`.

It warns for old references and maps `sigreturn` to `compat_13_sigreturn13`.

The file is a syscall veneer, with comments noting register state preservation requirements.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat_sigreturn.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat_sigsuspend.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat_sigsuspend.S

Implements MIPS compatibility `sigsuspend`.

It loads the legacy integer mask from the pointer in `a0`, invokes `compat_13_sigsuspend13`, returns zero only on unexpected success, and tail-calls `__cerror` on normal interrupt/error paths.

This adapts pointer-style libc calls to the old signal-mask syscall.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/mips/sys/compat_sigsuspend.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/or1k/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/or1k/Makefile.inc

This file is empty.

It is an architecture compatibility build placeholder for OpenRISC/or1k.

No build inclusions or source behavior are defined.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/or1k/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/Makefile.inc

Build include fragment for PowerPC libc compatibility.

It includes the architecture `gen` and `sys` compatibility make fragments and adds `-I.` to `CPPFLAGS`.

No runtime behavior is present.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/Makefile.inc

Lists PowerPC compatibility syscall sources.

The list includes legacy `vfork`, signal return/trampoline, SysV IPC wrappers, signal ABI wrappers, and `quotactl`.

This is build metadata only.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat_Ovfork.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat_Ovfork.S

Implements PowerPC legacy `vfork`.

After the syscall, it adjusts `r4` from the kernel parent/child indicator and masks `r3` so the child returns zero and the parent returns the child pid.

This preserves old process-control ABI behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat_Ovfork.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat___semctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat___semctl.S

Defines PowerPC compatibility `__semctl`.

It maps `__semctl` to `compat_14___semctl` using the syscall `PSEUDO` macro.

This is System V semaphore ABI compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat___semctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat___sigreturn14.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat___sigreturn14.S

Defines PowerPC `__sigreturn14`.

It is a minimal `PSEUDO(__sigreturn14, compat_16___sigreturn14)` veneer.

Used by the PowerPC legacy signal trampoline.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat___sigreturn14.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat___sigtramp1.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat___sigtramp1.S

Implements PowerPC `__sigtramp_sigcontext_1`.

On entry, `r3/r4/r5` contain signal number/code/sigcontext pointer and `lr` contains the handler address. The trampoline allocates a call frame, calls the handler with `blrl`, computes the sigcontext address, calls `compat_16___sigreturn14`, and exits if sigreturn fails.

This is architecture-specific signal ABI compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat___sigtramp1.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat_msgctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat_msgctl.S

Defines PowerPC compatibility `msgctl`.

It emits the standard compatibility warning and maps to `compat_14_msgctl`.

No filesystem behavior is present.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat_msgctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat_quotactl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat_quotactl.S

Defines PowerPC compatibility `quotactl`.

It warns callers to include `<sys/quota.h>` and routes the symbol to `compat_50_quotactl`.

This is directly relevant to filesystem quota ABI compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat_quotactl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat_shmctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat_shmctl.S

Defines PowerPC compatibility `shmctl`.

It warns about compatibility references and maps to `compat_14_shmctl`.

This is shared-memory ABI compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat_shmctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat_sigaction13.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat_sigaction13.S

Defines PowerPC compatibility `sigaction`.

It warns callers to include `<signal.h>` and maps `sigaction` to `compat_13_sigaction13`.

This is a minimal signal ABI veneer.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat_sigaction13.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat_sigpending13.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat_sigpending13.S

Implements PowerPC compatibility `sigpending`.

It saves the output pointer in `r5`, calls `compat_13_sigpending13`, stores the returned mask into `*r5`, returns zero on success, and branches to `__cerror` on syscall failure.

This adapts old integer signal masks to the pointer API.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat_sigpending13.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat_sigprocmask13.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat_sigprocmask13.S

Implements PowerPC compatibility `sigprocmask`.

If `set` is non-null it loads `*set` into the syscall argument; if null it uses `SIG_BLOCK`. It calls `compat_13_sigprocmask13`, optionally stores the returned old mask into `*oset`, and returns zero.

Errors branch to `__cerror`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat_sigprocmask13.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat_sigreturn13.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat_sigreturn13.S

Defines PowerPC compatibility `sigreturn`.

It emits a warning for old references and maps to `compat_13_sigreturn13`.

The file is a minimal syscall veneer.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat_sigreturn13.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat_sigsuspend13.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat_sigsuspend13.S

Implements PowerPC compatibility `sigsuspend`.

It loads the integer mask from the caller-provided pointer, invokes `compat_13_sigsuspend13`, and always branches to `__cerror` because successful return is not expected.

This is old signal-mask compatibility glue.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc/sys/compat_sigsuspend13.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc64/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc64/Makefile.inc

Build include fragment for PowerPC64 libc compatibility.

It includes the architecture `gen` and `sys` compatibility fragments.

No runtime code is defined.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc64/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc64/sys/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc64/sys/Makefile.inc

Lists PowerPC64 compatibility syscall sources.

The included objects cover `msgctl`, `__semctl`, `shmctl`, `quotactl`, and `compat_missing.c`.

This architecture uses C shims for several missing legacy signal symbols instead of the fuller assembly set present on 32-bit PowerPC.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc64/sys/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc64/sys/compat___semctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc64/sys/compat___semctl.S

Defines PowerPC64 compatibility `__semctl`.

It maps `__semctl` to `compat_14___semctl`.

This is System V semaphore compatibility glue.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc64/sys/compat___semctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc64/sys/compat_missing.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc64/sys/compat_missing.c

Defines compatibility symbols that autoconf or old code may probe without including the modern standard headers.

It declares warning references for `sigaction`, `sigpending`, `sigprocmask`, and `sigsuspend`, then implements these public symbols as forwarding C functions to modern/internal NetBSD signal APIs: `__sigaction_siginfo`, `__sigpending14`, `__sigprocmask14`, and `__sigsuspend14`.

This is PowerPC64-specific ABI surface completion for old signal APIs.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc64/sys/compat_missing.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc64/sys/compat_msgctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc64/sys/compat_msgctl.S

Defines PowerPC64 compatibility `msgctl`.

It emits a warning and maps to `compat_14_msgctl`.

This is SysV message queue ABI compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc64/sys/compat_msgctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc64/sys/compat_quotactl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc64/sys/compat_quotactl.S

Defines PowerPC64 compatibility `quotactl`.

It warns about old references and maps to `compat_50_quotactl`.

This preserves old filesystem quota-control ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc64/sys/compat_quotactl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc64/sys/compat_shmctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc64/sys/compat_shmctl.S

Defines PowerPC64 compatibility `shmctl`.

It emits a warning and maps to `compat_14_shmctl`.

This is shared-memory ABI compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/powerpc64/sys/compat_shmctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/Makefile.inc

Build include fragment for RISC-V libc compatibility.

It includes only `${COMPATARCHDIR}/sys/Makefile.inc`.

No generated compatibility fragment is included here.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/Makefile.inc

Lists RISC-V compatibility syscall sources.

The list includes simple veneers for legacy `vfork`, SysV IPC controls, `quotactl`, and signal APIs.

This is build metadata only.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/compat_Ovfork.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/compat_Ovfork.S

Defines RISC-V compatibility `vfork`.

The file is public-domain and maps `vfork` to `__vfork14` while emitting a warning for old references.

This is a simple syscall alias veneer.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/compat_Ovfork.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/compat_msgctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/compat_msgctl.S

Defines RISC-V compatibility `msgctl`.

It warns callers to include `<sys/msg.h>` and maps to `compat_14_msgctl`.

This is a simple public-domain compatibility wrapper.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/compat_msgctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/compat_quotactl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/compat_quotactl.S

Defines RISC-V compatibility `quotactl`.

It warns callers to include `<sys/quota.h>` and maps to `compat_50_quotactl`.

Filesystem relevance is direct through quota control.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/compat_quotactl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/compat_shmctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/compat_shmctl.S

Defines RISC-V compatibility `shmctl`.

It warns callers to include `<sys/shm.h>` and maps to `compat_14_shmctl`.

This is a simple shared-memory compatibility veneer.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/compat_shmctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/compat_sigaction.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/compat_sigaction.S

Defines RISC-V compatibility `sigaction`.

It warns callers to include `<signal.h>` and maps to `compat_13_sigaction13`.

This preserves old signal action ABI names.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/compat_sigaction.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/compat_sigpending.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/compat_sigpending.S

Defines RISC-V compatibility `sigpending`.

It emits the standard compatibility warning and maps directly to `compat_13_sigpending13`.

Unlike older architectures, this file does not perform pointer-to-integer mask adaptation in assembly.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/compat_sigpending.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/compat_sigprocmask.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/compat_sigprocmask.S

Defines RISC-V compatibility `sigprocmask`.

It warns callers to include `<signal.h>` and maps to `compat_13_sigprocmask13`.

This is a minimal syscall alias.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/compat_sigprocmask.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/compat_sigreturn.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/compat_sigreturn.S

Defines RISC-V compatibility `sigreturn`.

It emits a warning and maps to `compat_13_sigreturn13`.

This is a minimal legacy signal-return veneer.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/compat_sigreturn.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/compat_sigsuspend.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/compat_sigsuspend.S

Defines RISC-V compatibility `sigsuspend`.

It warns callers to include `<signal.h>` and maps to `compat_13_sigsuspend13`.

This is a simple legacy signal-mask wrapper.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/riscv/sys/compat_sigsuspend.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/Makefile.inc

Build include fragment for SH3 libc compatibility.

It includes architecture `gen` and `sys` compatibility make fragments.

No runtime code is present.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/Makefile.inc

Lists SH3 compatibility syscall source files.

The list includes legacy `vfork`, `__semctl`, signal return/trampoline, SysV IPC, signal wrappers, and `quotactl`.

This is build metadata.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat_Ovfork.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat_Ovfork.S

Implements SH3 compatibility `vfork`.

It uses `trapa #0x80` with `SYS_vfork`, interprets `r1` as parent/child indicator, and masks `r0` so the child returns zero and the parent returns the child pid.

Errors jump to `CERROR`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat_Ovfork.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat___semctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat___semctl.S

Defines SH3 compatibility `__semctl`.

It maps `__semctl` to `compat_14___semctl`.

This is System V semaphore compatibility glue.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat___semctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat___sigreturn14.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat___sigreturn14.S

Defines SH3 compatibility `__sigreturn14`.

The file preserves old Berkeley-derived signal-return ABI metadata and maps `__sigreturn14` to `compat_16___sigreturn14`.

It is used by the SH3 signal trampoline.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat___sigreturn14.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat___sigtramp1.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat___sigtramp1.S

Implements SH3 `__sigtramp_sigcontext_1`.

The trampoline is invoked only after signal handler return; it passes `r15` as the sigcontext pointer to `compat_16___sigreturn14`, then exits with errno if sigreturn fails.

This supports old SH signal-delivery ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat___sigtramp1.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat_msgctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat_msgctl.S

Defines SH3 compatibility `msgctl`.

It warns callers to include `<sys/msg.h>` and maps to `compat_14_msgctl`.

This is SysV message queue compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat_msgctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat_quotactl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat_quotactl.S

Defines SH3 compatibility `quotactl`.

It warns callers to include `<sys/quota.h>` and maps to `compat_50_quotactl`.

This preserves old filesystem quota-control ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat_quotactl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat_shmctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat_shmctl.S

Defines SH3 compatibility `shmctl`.

It warns callers to include `<sys/shm.h>` and maps to `compat_14_shmctl`.

This is shared-memory ABI compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat_shmctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat_sigaction.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat_sigaction.S

Defines SH3 compatibility `sigaction`.

It emits the standard signal-header warning and maps to `compat_13_sigaction13`.

This is a minimal signal ABI veneer.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat_sigaction.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat_sigpending.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat_sigpending.S

Implements SH3 compatibility `sigpending`.

After `_SYSCALL(sigpending, compat_13_sigpending13)`, it stores the returned mask into `@r4`, clears `r0`, and returns.

This adapts the legacy integer mask result to the caller’s pointer output.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat_sigpending.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat_sigprocmask.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat_sigprocmask.S

Implements SH3 compatibility `sigprocmask`.

It tests whether `set` is null, substitutes `SIG_BLOCK` for null masks, otherwise loads `*set`, invokes `SYS_compat_13_sigprocmask13`, and optionally stores the returned old mask to `*oset`.

Errors jump to `CERROR`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat_sigprocmask.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat_sigreturn.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat_sigreturn.S

Defines SH3 compatibility `sigreturn`.

It warns about old references and maps to `compat_13_sigreturn13`.

The file preserves old signal-return ABI behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat_sigreturn.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat_sigsuspend.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat_sigsuspend.S

Implements SH3 compatibility `sigsuspend`.

It loads the integer signal mask from `@r4`, invokes `SYS_compat_13_sigsuspend13`, returns zero only on unexpected success, and jumps to `CERROR` on normal error/interrupt.

This is old signal-mask ABI glue.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sh3/sys/compat_sigsuspend.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/Makefile.inc

Build include fragment for SPARC libc compatibility.

It includes architecture `gen` and `sys` fragments.

No runtime behavior is defined here.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/Makefile.inc

Lists SPARC compatibility syscall source files.

The set includes `vfork`, `__semctl`, `__sigreturn14`, a large sigcontext trampoline, SysV IPC controls, signal wrappers, and `quotactl`.

This is build metadata.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat_Ovfork.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat_Ovfork.S

Implements SPARC compatibility `vfork`.

It uses the kernel-provided `%o1` parent/child indicator, decrements it, and masks `%o0` so child returns zero while parent returns the child pid.

This is old process-control ABI compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat_Ovfork.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat___semctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat___semctl.S

Defines SPARC compatibility `__semctl`.

It maps `__semctl` to `compat_14___semctl`.

This is System V semaphore ABI compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat___semctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat___sigreturn14.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat___sigreturn14.S

Implements SPARC `__sigreturn14`.

It loads `SYS_compat_16___sigreturn14` into `%g1`, traps through `ST_SYSCALL`, and falls into `ERROR()` if the syscall returns.

This supports the old sigcontext trampoline path.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat___sigreturn14.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat___sigtramp1.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat___sigtramp1.S

Implements the SPARC `__sigtramp_sigcontext_1` legacy signal trampoline.

It documents the signal stack layout, saves global registers and `%y`, conditionally saves FPU state when enabled, calls the handler through `%g1`, restores saved state, then invokes `compat_16___sigreturn14`. If sigreturn fails, it calls `exit`.

This is one of the more complex files in the group because SPARC register windows and FPU state require careful trampoline preservation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat___sigtramp1.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat_msgctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat_msgctl.S

Defines SPARC compatibility `msgctl`.

It warns callers to include `<sys/msg.h>` and maps to `compat_14_msgctl`.

This is SysV message queue ABI compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat_msgctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat_quotactl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat_quotactl.S

Defines SPARC compatibility `quotactl`.

It warns callers to include `<sys/quota.h>` and maps to `compat_50_quotactl`.

This is filesystem quota compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat_quotactl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat_shmctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat_shmctl.S

Defines SPARC compatibility `shmctl`.

It warns callers to include `<sys/shm.h>` and maps to `compat_14_shmctl`.

This is shared-memory ABI compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat_shmctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat_sigaction.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat_sigaction.S

Defines SPARC compatibility `sigaction`.

It emits the standard warning and maps to `compat_13_sigaction13`.

This preserves legacy signal-action ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat_sigaction.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat_sigpending.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat_sigpending.S

Implements SPARC compatibility `sigpending`.

It saves the output pointer in `%o2`, invokes `SYS_compat_13_sigpending13`, stores the returned mask through the saved pointer on success, and returns zero.

On failure it enters the standard `ERROR()` path.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat_sigpending.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat_sigprocmask.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat_sigprocmask.S

Implements SPARC compatibility `sigprocmask`.

It dereferences `set` into `%o1` when non-null, otherwise uses `SIG_BLOCK`, invokes `SYS_compat_13_sigprocmask13`, and optionally stores the returned old mask into `*oset`.

This adapts modern pointer arguments to the old integer mask syscall.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat_sigprocmask.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat_sigreturn.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat_sigreturn.S

Implements SPARC compatibility `sigreturn`.

It loads `SYS_compat_13_sigreturn13` into `%g1`, traps via `ST_SYSCALL`, and enters `ERROR()` if it returns.

This is a direct old signal-return syscall entry.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat_sigreturn.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat_sigsuspend.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat_sigsuspend.S

Implements SPARC compatibility `sigsuspend`.

It loads the integer mask from the pointer in `%o0`, invokes `SYS_compat_13_sigsuspend13`, and uses `ERROR()` because the syscall normally returns through interruption.

This is legacy signal-mask compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc/sys/compat_sigsuspend.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/Makefile.inc

Build include fragment for SPARC64 libc compatibility.

It includes architecture `gen` and `sys` compatibility fragments.

No runtime behavior is defined.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/Makefile.inc

Lists SPARC64 compatibility syscall source files.

The source set mirrors SPARC: `vfork`, `__semctl`, signal return/trampoline, SysV IPC controls, signal wrappers, and `quotactl`.

This is build metadata.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat_Ovfork.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat_Ovfork.S

Implements SPARC64 compatibility `vfork`.

It decrements `%o1` and masks `%o0` to produce zero in the child and child pid in the parent.

This is old process-control ABI compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat_Ovfork.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat___semctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat___semctl.S

Defines SPARC64 compatibility `__semctl`.

It maps `__semctl` to `compat_14___semctl`.

This is System V semaphore ABI compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat___semctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat___sigreturn14.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat___sigreturn14.S

Implements SPARC64 `__sigreturn14`.

It loads `SYS_compat_16___sigreturn14`, traps via `ST_SYSCALL`, and enters `ERROR()` if control returns.

Used by the legacy sigcontext trampoline.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat___sigreturn14.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat___sigtramp1.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat___sigtramp1.S

Implements the SPARC64 `__sigtramp_sigcontext_1` legacy signal trampoline.

It documents the 64-bit signal stack layout, saves global registers, checks dirty FPU register state with `%fprs`, saves/restores FPU blocks using block load/store ASIs, preserves `%y`, calls the handler via `%g1`, then invokes `compat_16___sigreturn14`. If sigreturn fails, it exits.

This is architecture-specific compatibility code with careful register-window and floating-point preservation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat___sigtramp1.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat_msgctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat_msgctl.S

Defines SPARC64 compatibility `msgctl`.

It warns callers to include `<sys/msg.h>` and maps to `compat_14_msgctl`.

This is SysV message queue compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat_msgctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat_quotactl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat_quotactl.S

Defines SPARC64 compatibility `quotactl`.

It warns callers to include `<sys/quota.h>` and maps to `compat_50_quotactl`.

This preserves old filesystem quota ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat_quotactl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat_shmctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat_shmctl.S

Defines SPARC64 compatibility `shmctl`.

It warns callers to include `<sys/shm.h>` and maps to `compat_14_shmctl`.

This is shared-memory ABI compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat_shmctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat_sigaction.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat_sigaction.S

Defines SPARC64 compatibility `sigaction`.

It emits the standard warning and maps to `compat_13_sigaction13`.

This is a minimal legacy signal-action wrapper.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat_sigaction.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat_sigpending.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat_sigpending.S

Implements SPARC64 compatibility `sigpending`.

It saves the output pointer in `%o2`, invokes `SYS_compat_13_sigpending13`, stores the returned mask into `*%o2` on success, and returns zero.

Failures enter `ERROR()`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat_sigpending.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat_sigprocmask.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat_sigprocmask.S

Implements SPARC64 compatibility `sigprocmask`.

It dereferences a non-null `set` pointer into `%o1`, otherwise sets `%o0` to `SIG_BLOCK`, invokes `SYS_compat_13_sigprocmask13`, and optionally stores the returned old mask through `oset`.

This adapts pointer-style libc arguments to the old integer mask syscall.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat_sigprocmask.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat_sigreturn.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat_sigreturn.S

Implements SPARC64 compatibility `sigreturn`.

It loads `SYS_compat_13_sigreturn13`, traps through `ST_SYSCALL`, and enters `ERROR()` if the syscall returns.

This is a direct legacy signal-return entry.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat_sigreturn.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat_sigsuspend.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat_sigsuspend.S

Implements SPARC64 compatibility `sigsuspend`.

It loads the integer mask from the pointer in `%o0`, invokes `SYS_compat_13_sigsuspend13`, and uses `ERROR()` because the syscall normally returns by interruption.

This is legacy signal-mask compatibility glue.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/sparc64/sys/compat_sigsuspend.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/Makefile.inc

Build include fragment for VAX libc compatibility.

It includes only `${COMPATARCHDIR}/sys/Makefile.inc`.

No runtime behavior is defined.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/Makefile.inc

Lists VAX compatibility syscall source files.

The set includes legacy `vfork`, signal return/trampoline, SysV IPC wrappers, old signal APIs, and `quotactl`.

This is build metadata.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat_Ovfork.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat_Ovfork.S

Implements VAX compatibility `vfork`.

It uses a VAX-specific stack/return-address trick: saves the caller return address, rewrites the frame return address to a local label, returns before issuing `chmk $SYS_vfork`, then jumps indirectly through the saved return address. Child/parent return values are fixed with `mnegl` and `bicl2`.

The error path handles both reentrant and non-reentrant errno storage.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat_Ovfork.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat___semctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat___semctl.S

Defines VAX compatibility `__semctl`.

It maps `__semctl` to `compat_14___semctl`.

This is System V semaphore ABI compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat___semctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat___sigreturn14.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat___sigreturn14.S

Defines VAX compatibility `__sigreturn14`.

It maps `__sigreturn14` to `compat_16___sigreturn14` and adjusts the profiling `ENTRY` macro under `GPROF` to preserve registers.

This supports VAX legacy signal return.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat___sigreturn14.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat___sigtramp2.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat___sigtramp2.S

Implements VAX `__sigtramp_sigcontext_2`.

The trampoline saves scratch registers, calls the handler with `callg (%ap),(%fp)`, restores registers, adjusts `ap` to point at the sigcontext argument, invokes `compat_16___sigreturn14`, and halts if control returns.

This is a VAX-specific legacy signal trampoline.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat___sigtramp2.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat_msgctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat_msgctl.S

Defines VAX compatibility `msgctl`.

It warns callers to include `<sys/msg.h>` and maps to `compat_14_msgctl`.

This is SysV message queue ABI compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat_msgctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat_quotactl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat_quotactl.S

Defines VAX compatibility `quotactl`.

It warns callers to include `<sys/quota.h>` and maps to `compat_50_quotactl`.

This is filesystem quota compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat_quotactl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat_shmctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat_shmctl.S

Defines VAX compatibility `shmctl`.

It warns callers to include `<sys/shm.h>` and maps to `compat_14_shmctl`.

This is shared-memory ABI compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat_shmctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat_sigaction13.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat_sigaction13.S

Defines VAX compatibility `sigaction`.

It emits the standard signal-header warning and maps to `compat_13_sigaction13`.

This is a legacy signal-action wrapper.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat_sigaction13.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat_sigpending13.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat_sigpending13.S

Implements VAX compatibility `sigpending`.

After `_SYSCALL(sigpending, compat_13_sigpending13)`, it stores `%r0` through the pointer at `4(%ap)`, clears `%r0`, and returns.

This adapts the old integer mask result to the pointer output API.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat_sigpending13.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat_sigprocmask13.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat_sigprocmask13.S

Implements VAX compatibility `sigprocmask`.

It dereferences the new mask pointer when non-null, substitutes `SIG_BLOCK` when null, invokes `SYS_compat_13_sigprocmask13`, and optionally stores the returned old mask through the output pointer.

Errors jump to `CERROR+2`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat_sigprocmask13.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat_sigreturn13.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat_sigreturn13.S

Defines VAX compatibility `sigreturn`.

It maps `sigreturn` to `compat_13_sigreturn13` and includes profiling safeguards that preserve registers under `GPROF`.

This is legacy signal-return ABI support.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat_sigreturn13.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat_sigsuspend13.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat_sigsuspend13.S

Implements VAX compatibility `sigsuspend`.

It dereferences the signal-mask pointer into the syscall argument, invokes `compat_13_sigsuspend13`, and returns zero only on unexpected success; errors jump to `CERROR+2`.

This bridges pointer-style libc calls to the old integer-mask syscall.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/vax/sys/compat_sigsuspend13.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/Makefile.inc

Build include fragment for x86_64 libc compatibility.

It includes `gen/Makefile.inc`, and includes `sys/Makefile.inc` only when `${RUMPRUN} != "yes"`.

This conditional avoids pulling syscall compatibility assembly into rump-run builds.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/Makefile.inc

Lists x86_64 compatibility syscall sources.

The set includes legacy `vfork`, `__semctl`, empty old signal-return stubs, SysV IPC controls, signal-mask wrappers, and `quotactl`.

This is build metadata.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/compat_Ovfork.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/compat_Ovfork.S

Implements x86_64 compatibility `vfork`.

It pops the return address into `%r9`, invokes the `vfork` syscall, fixes parent/child return values using `%edx` and `%eax`, and jumps to the saved return address. The error path restores the return address and jumps to `CERROR`, with PIC support.

This preserves old `vfork` calling behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/compat_Ovfork.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/compat___semctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/compat___semctl.S

Defines x86_64 compatibility `__semctl`.

It maps `__semctl` to `compat_14___semctl`.

This is System V semaphore ABI compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/compat___semctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/compat___sigreturn14.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/compat___sigreturn14.S

This x86_64 file is intentionally an empty compatibility stub.

Its comment says NetBSD 1.6 binary compatibility is not needed on this architecture.

No symbols or syscall wrappers are emitted beyond metadata/includes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/compat___sigreturn14.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/compat_msgctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/compat_msgctl.S

Defines x86_64 compatibility `msgctl`.

It warns callers to include `<sys/msg.h>` and maps to `compat_14_msgctl`.

This is SysV message queue ABI compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/compat_msgctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/compat_quotactl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/compat_quotactl.S

Defines x86_64 compatibility `quotactl`.

It warns callers to include `<sys/quota.h>` and maps to `compat_50_quotactl`.

This is filesystem quota compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/compat_quotactl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/compat_shmctl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/compat_shmctl.S

Defines x86_64 compatibility `shmctl`.

It warns callers to include `<sys/shm.h>` and maps to `compat_14_shmctl`.

This is shared-memory ABI compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/compat_shmctl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/compat_sigaction.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/compat_sigaction.S

Defines x86_64 compatibility `sigaction`.

It emits the standard warning and maps to `compat_13_sigaction13`.

This is legacy signal-action ABI support.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/compat_sigaction.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/compat_sigpending.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/compat_sigpending.S

Implements x86_64 compatibility `sigpending`.

After `_SYSCALL(sigpending, compat_13_sigpending13)`, it stores `%eax` into the caller-provided pointer in `%rdi`, clears `%eax`, and returns.

This adapts an old integer mask result to pointer output.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/compat_sigpending.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/compat_sigprocmask.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/compat_sigprocmask.S

Implements x86_64 compatibility `sigprocmask`.

It checks whether `%rsi` (`set`) is null, substitutes `SIG_BLOCK` when null, otherwise loads `*set` into `%esi`, calls `compat_13_sigprocmask13`, and optionally stores the returned old mask through `%rdx`.

Errors jump to `CERROR`, with PIC handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/compat_sigprocmask.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/compat_sigreturn.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/compat_sigreturn.S

This x86_64 file is intentionally empty.

Its comment says NetBSD 1.3 binary compatibility is not needed.

No runtime wrapper is emitted.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/compat_sigreturn.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/compat_sigsuspend.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/compat_sigsuspend.S

Implements x86_64 compatibility `sigsuspend`.

It loads the integer signal mask from `(%rdi)`, invokes `compat_13_sigsuspend13`, returns zero only on unexpected success, and jumps to `CERROR` on error, with PIC handling.

This bridges pointer-style libc calls to the old signal-mask syscall.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/arch/x86_64/sys/compat_sigsuspend.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/db/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/db/Makefile.inc

Build include fragment for libc database compatibility code.

It includes `${COMPATDIR}/db/hash/Makefile.inc`.

No runtime code is defined here.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/db/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/db/hash/Makefile.inc -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/db/hash/Makefile.inc

Build fragment for compatibility hash database code.

It adds `${COMPATDIR}/db/hash` to `.PATH` and adds `compat_ndbmdatum.c` to `SRCS`.

This wires old NDBM datum compatibility into libc.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/db/hash/Makefile.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/db/hash/compat_ndbmdatum.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/db/hash/compat_ndbmdatum.c

Builds compatibility versions of NDBM datum APIs using the old `datum12` layout.

It defines `__LIBC12_SOURCE__`, includes both modern `<ndbm.h>` and compatibility `<compat/include/ndbm.h>`, emits warnings for old `dbm_*` references, renames `datum` to `datum12`, and clamps datum sizes to `INT_MAX`.

It then includes the shared implementation `db/hash/ndbmdatum.c` under these compatibility definitions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/db/hash/compat_ndbmdatum.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/aio.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/aio.h

Declares compatibility AIO timeout interfaces.

It forward-declares `struct aiocb`, `struct timespec50`, and `struct timespec`, then declares old `aio_suspend` using `timespec50` and modern `__aio_suspend50` using `timespec`.

This supports time32/time64 ABI translation for asynchronous I/O.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/aio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/dirent.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/dirent.h

Declares compatibility directory APIs using `struct dirent12`.

It maps old `opendir`, `readdir`, `readdir_r`, `_readdir_unlocked`, `scandir`, `getdents`, `alphasort`, and `getdirentries` declarations alongside modern `__*30` variants.

Filesystem relevance is direct: this header preserves old directory-entry ABI for filesystem traversal.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/dirent.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/errno.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/errno.h

Declares old global errno description symbols.

It exposes `sys_nerr` and `sys_errlist[]` inside `__BEGIN_DECLS`.

This preserves ABI for old programs that referenced the historical error-list variables.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/errno.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/extern.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/extern.h

Declares compatibility syslog entry points.

It forward-declares `struct syslog_data60` and declares `syslog_ss`, `vsyslog_ss`, `syslogp_ss`, and `vsyslogp_ss` with printf-like attributes, plus `__cmsg_alignbytes`.

This is libc compatibility surface for older syslog/control-message ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/extern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/fstypes.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/fstypes.h

Defines old fixed-size file handle types used up through NetBSD 3.x.

It declares `struct compat_30_fid`, `struct compat_30_fhandle`, and `FHANDLE30_SIZE`.

Filesystem relevance is direct: these structures preserve old exported file-handle ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/fstypes.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/fts.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/fts.h

Declares compatibility FTS traversal APIs.

It exposes `fts_children`, `fts_close`, `fts_open`, `fts_read`, and `fts_set` using legacy `FTS`/`FTSENT` ABI declarations.

Filesystem relevance is direct through directory tree traversal.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/fts.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/glob.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/glob.h

Declares compatibility globbing APIs.

It exposes old `glob` and `globfree` declarations using `glob_t`.

Filesystem relevance is direct: pathname expansion depends on directory traversal and stat-like filesystem behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/glob.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/locale.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/locale.h

Declares compatibility locale APIs.

It defines old `_LC_LAST` as `7`, declares `setlocale`, `__setlocale_mb_len_max_32`, and `compat_setlocale` renamed to `setlocale`.

This preserves older locale ABI, especially around multibyte locale evolution.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/locale.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/lwp.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/lwp.h

Declares compatibility lightweight-process park APIs.

It exposes `_lwp_park` with `timespec50`, `___lwp_park50` with `timespec`, and `___lwp_park60` with clock id/flags plus `timespec`.

This is time ABI compatibility for threading primitives.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/lwp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/mqueue.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/mqueue.h

Declares compatibility POSIX message queue timed operations.

It exposes old `mq_timedreceive` and `mq_timedsend` using `timespec50`, plus modern `__mq_timedreceive50` and `__mq_timedsend50` using `timespec`.

This is time32/time64 compatibility for message queues.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/mqueue.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/ndbm.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/ndbm.h

Defines the old `datum12` NDBM data structure.

`datum12` stores `void *dptr` and `int dsize`; the header declares old `dbm_delete`, `dbm_fetch`, `dbm_firstkey`, `dbm_nextkey`, and `dbm_store`.

This preserves the older database record ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/ndbm.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/ns.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/ns.h

Defines old Xerox Network Systems address structures.

It declares `union ns_host`, `union ns_net`, `union ns_net_u`, `struct ns_addr`, and compatibility declarations for `ns_addr()` and `ns_ntoa()`.

This is network ABI compatibility, not filesystem logic.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/ns.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/pwd.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/pwd.h

Defines `struct passwd50` with 32-bit `pw_change` and `pw_expire` fields, plus inline converters between modern `struct passwd` and `passwd50`.

It declares old password database APIs returning or filling `passwd50`, and corresponding modern `__*50` APIs using `struct passwd`.

Filesystem relevance is indirect: passwd records include home directories and shells and are commonly consumed by filesystem utilities.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/pwd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/rpc/pmap_clnt.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/rpc/pmap_clnt.h

Declares compatibility RPC portmapper client remote-call APIs.

It exposes old `pmap_rmtcall` using `struct timeval50` and modern `__pmap_rmtcall50` using `struct timeval`.

This is RPC time ABI compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/rpc/pmap_clnt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/rpc/rpcb_clnt.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/rpc/rpcb_clnt.h

Declares compatibility RPC binder client APIs.

It exposes old `rpcb_rmtcall` using `timeval50`, old `rpcb_gettime` using `int32_t *`, and modern `__rpcb_rmtcall50` / `__rpcb_gettime50` variants.

This preserves RPC time-related ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/rpc/rpcb_clnt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/sched.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/sched.h

Declares compatibility scheduler interval API.

It includes scheduler and compatibility time headers, then declares `sched_rr_get_interval(pid_t, struct timespec50 *)`.

This is time ABI compatibility for POSIX scheduling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/sched.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/setjmp.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/setjmp.h

Declares old setjmp/longjmp compatibility entry points.

It exposes `__setjmp14`, `__longjmp14`, `__sigsetjmp14`, and `__siglongjmp14` with `__returns_twice` / `__dead` attributes.

This preserves old nonlocal-jump ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/setjmp.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/signal.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/signal.h

Declares old signal ABI types and functions.

It includes `<compat/sys/signal.h>`, declares old and modern variants for `sigaction`, signal-set manipulation, `sigpending`, `sigprocmask`, `sigsuspend`, timed signal wait, `sigaltstack`, and trampoline symbols derived from `__SIGTRAMP_*_VERSION`.

This header is the central libc compatibility surface for legacy signal behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/signal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/stdio.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/stdio.h

Declares compatibility stdio file-position APIs.

It exposes old `fgetpos(FILE *, off_t *)` and `fsetpos(FILE *, const off_t *)`.

Filesystem relevance is direct through file stream positioning ABI.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/stdio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/stdlib.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/stdlib.h

Declares assorted compatibility stdlib APIs.

It includes old and modern variants for `unsetenv`, `putenv`, `devname`, `initstate`, and `srandom`, preserving historical argument types such as `int32_t dev` and `unsigned long` seeds.

Filesystem relevance is direct for `devname`, which maps device numbers to names.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/stdlib.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/time.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/time.h

Declares old time and time-zone compatibility APIs.

It includes `<compat/sys/time.h>`, defines `CLK_TCK`, declares old 32-bit-time functions such as `ctime`, `gmtime`, `localtime`, `time`, `mktime`, and many `_r`/timezone variants, plus modern `__*50` clock, nanosleep, and timer functions using `struct timespec`.

This is a broad time32/time64 ABI compatibility header used across old libc consumers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libc/compat/include/time.h -->