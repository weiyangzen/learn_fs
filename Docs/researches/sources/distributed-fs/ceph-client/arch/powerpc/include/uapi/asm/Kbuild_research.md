<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/Kbuild

Purpose: Lists generated PowerPC UAPI syscall-number headers for export.

Important APIs/types/functions: `generated-y += unistd_32.h` and `generated-y += unistd_64.h`.

Control flow: During headers generation, Kbuild emits both 32-bit and 64-bit syscall tables for UAPI installation.

State and persistence: No runtime state; generated header presence persists in the exported headers tree.

Dependencies and integration points: Depends on the kernel UAPI header generation pipeline and syscall table generation.

Risks: Omitting either generated header breaks userspace builds for that ABI.

Test signals: Run `make headers_install` and compile trivial programs including `<asm/unistd.h>` for ppc32 and ppc64.

Source read size: 3 lines, 89 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/Kbuild -->
