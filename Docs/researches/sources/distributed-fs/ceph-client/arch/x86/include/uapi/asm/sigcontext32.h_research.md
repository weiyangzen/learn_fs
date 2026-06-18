<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/sigcontext32.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/sigcontext32.h

Purpose: Legacy compatibility wrapper that redirects 32-bit sigcontext includes to the unified `sigcontext.h` definitions.

Important APIs/types/functions: Inclusion of `asm/sigcontext.h`.

Control flow: No runtime flow; preprocessing makes older include paths see the current definitions.

State and persistence behavior: No state. Preserves include-level ABI compatibility.

Dependencies and integration points: Integrates with older userspace code, 32-bit signal ABI, and libc headers expecting `<asm/sigcontext32.h>`.

Risks and test signals: Risks are include recursion or missing legacy path. Test userspace builds that include this header directly and 32-bit signal ABI selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/sigcontext32.h -->
