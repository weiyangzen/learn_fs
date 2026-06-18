<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/psrcompat.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/psrcompat.h

Purpose: Converts between 64-bit V9 `tstate` condition state and old 32-bit PSR-compatible views for compat code.

Important APIs and control flow: duplicates V8 PSR masks, defines fake `PSR_V8PLUS` and `PSR_XCC`, and provides `tstate_to_psr()` and `psr_to_tstate_icc()` inline conversions. The conversion maps CWP, supervisor bit, ICC, optional XCC, syscall marker, and the V8PLUS marker.

State, dependencies, and risks: state is signal/ptrace-visible register condition codes during 32-bit compatibility on 64-bit kernels. Dependencies include `asm/pstate.h`. Risks are lost condition-code bits, incorrect syscall marker preservation, and debugger/signal-frame ABI regressions. Test signals are 32-bit process ptrace, signal return, condition-code-sensitive single stepping, and V8PLUS userspace tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/psrcompat.h -->
