<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/posix_types.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/posix_types.h

Purpose: Routes userspace POSIX type definitions to the correct x86 ABI-specific header: i386, x32, or x86_64.

Important APIs/types/functions: Includes `posix_types_32.h`, `posix_types_x32.h`, or `posix_types_64.h` when not building the kernel.

Control flow: Preprocessor selection depends on `__i386__` and `__ILP32__`; no runtime flow.

State and persistence behavior: No runtime state. Selected typedefs determine userspace ABI structure layouts.

Dependencies and integration points: Integrates with libc, generic UAPI types, IPC/stat/signal headers, and x32 compatibility.

Risks and test signals: Risks are wrong ABI branch selection and namespace pollution for userspace. Test header compilation under i386, x86_64, and x32 targets and ABI struct size checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/posix_types.h -->
