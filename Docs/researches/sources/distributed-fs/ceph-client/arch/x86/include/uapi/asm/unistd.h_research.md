<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/unistd.h

Purpose: Defines the x32 syscall-number marker bit and selects the ABI-specific generated syscall-number header for userspace.

Important APIs/types/functions: `__X32_SYSCALL_BIT` and includes of `unistd_32.h`, `unistd_x32.h`, or `unistd_64.h`.

Control flow: Userspace preprocessing selects syscall numbers by target ABI. Runtime syscall wrappers use `__X32_SYSCALL_BIT` to identify x32 syscalls.

State and persistence behavior: No state. Syscall numbers are a stable userspace/kernel ABI.

Dependencies and integration points: Integrates with generated syscall headers, libc syscall wrappers, seccomp filters, strace, audit, and x32 compatibility.

Risks and test signals: Risks include missing generated headers, wrong x32 bit type/branch, and syscall-number table drift. Test `headers_install`, libc builds for all x86 ABIs, seccomp/strace decoding, and syscall table selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/unistd.h -->
