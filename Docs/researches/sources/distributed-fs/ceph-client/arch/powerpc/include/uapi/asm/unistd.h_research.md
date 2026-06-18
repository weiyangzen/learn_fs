<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/unistd.h

Purpose: Selects generated PowerPC syscall number header for 32-bit or 64-bit userspace.

Important APIs/types/functions: Includes `asm/unistd_32.h` unless `__powerpc64__`, otherwise `asm/unistd_64.h`.

Control flow: Userspace/kernel UAPI inclusion resolves syscall numbers at compile time for the target ABI.

State and persistence: No runtime state; syscall numbers are ABI constants.

Dependencies and integration points: Depends on generated headers declared in UAPI Kbuild.

Risks: Wrong ABI selection gives callers invalid syscall numbers.

Test signals: Headers-install tests and syscall-number compile checks for ppc32 and ppc64.

Source read size: 19 lines, 577 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/unistd.h -->
