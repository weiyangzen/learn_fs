<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/bitsperlong.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/bitsperlong.h

Purpose: Selects PowerPC userspace word size for generic type headers.

Important APIs/types/functions: Defines `__BITS_PER_LONG` as 64 for `__powerpc64__` and 32 otherwise, then includes the generic header.

Control flow: Preprocessor selection occurs when userspace includes UAPI type headers.

State and persistence: No runtime state; affects compile-time ABI layout.

Dependencies and integration points: Depends on compiler-defined `__powerpc64__` and `asm-generic/bitsperlong.h`.

Risks: Wrong word size breaks ioctl, stat, signal, and syscall ABI structures.

Test signals: Headers-install compile tests for ppc32 and ppc64 ABIs and sizeof checks for long-based structs.

Source read size: 13 lines, 312 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/bitsperlong.h -->
