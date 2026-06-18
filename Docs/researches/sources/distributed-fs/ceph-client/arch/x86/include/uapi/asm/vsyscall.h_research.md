<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/vsyscall.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/vsyscall.h

Purpose: Defines legacy x86_64 vsyscall numbers and the fixed vsyscall virtual address.

Important APIs/types/functions: `enum vsyscall_num` with `__NR_vgettimeofday`, `__NR_vtime`, `__NR_vgetcpu`, and `VSYSCALL_ADDR`.

Control flow: Legacy userspace can call fixed-address vsyscall entries; kernel may emulate, map, or fault them depending on configuration and security policy.

State and persistence behavior: No header-owned state. The fixed address is an ABI commitment for old binaries.

Dependencies and integration points: Integrates with x86_64 memory layout, vDSO/vsyscall compatibility, signal/fault handling, and seccomp/audit visibility of emulated calls.

Risks and test signals: Risks include breaking old binaries or weakening ASLR/security if mapped executable unexpectedly. Test legacy vsyscall binaries under emulate/native/none modes, `gettimeofday` compatibility, and fault behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/vsyscall.h -->
