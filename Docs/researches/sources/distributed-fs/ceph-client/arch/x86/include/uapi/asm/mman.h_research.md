<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/mman.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/mman.h

Purpose: Adds x86-specific `mmap` flags for low 32-bit placement and above-4G placement, then includes generic memory mapping flags.

Important APIs/types/functions: `MAP_32BIT`, `MAP_ABOVE4G`, and generic mman definitions.

Control flow: Userspace passes these flags to mmap-like syscalls; kernel address-selection code constrains the mapping range accordingly.

State and persistence behavior: No state. Resulting VMAs persist in the process address space.

Dependencies and integration points: Integrates with x86 virtual memory layout, legacy JIT/runtime low-address assumptions, and generic mmap UAPI.

Risks and test signals: Risks include address-selection regressions, conflicts with ASLR, and unsupported flag handling on compat paths. Test mmap with both flags, ASLR-enabled processes, 32-bit compatibility, and VMA placement verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/mman.h -->
