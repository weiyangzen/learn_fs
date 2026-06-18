<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/shmparam.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/shmparam.h

Purpose: defines x86 System V shared-memory alignment. Important macro is `SHMLBA`, typically tied to page size.

Control flow and state: generic SysV SHM code uses the alignment when attaching shared memory; the header has no runtime state. Dependencies are page size and generic IPC memory management. Risks are ABI-visible alignment changes affecting old applications. Test signals include SysV SHM attach/detach tests and compat ABI checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/shmparam.h -->
