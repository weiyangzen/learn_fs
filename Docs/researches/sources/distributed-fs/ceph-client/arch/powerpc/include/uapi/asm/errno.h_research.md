<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/errno.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/errno.h

Purpose: Overrides the generic `EDEADLOCK` value for PowerPC userspace ABI compatibility.

Important APIs/types/functions: Includes generic errno then redefines `EDEADLOCK` to 58.

Control flow: UAPI inclusion first clears any existing value, imports generic errno, and then applies the PowerPC-specific value.

State and persistence: No runtime state; numeric errno ABI persists in userspace programs.

Dependencies and integration points: Depends on `asm-generic/errno.h` and libc errno integration.

Risks: Changing the value breaks old binaries and source compatibility.

Test signals: Headers compile and errno numeric conformance checks for PowerPC libc.

Source read size: 11 lines, 278 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/errno.h -->
