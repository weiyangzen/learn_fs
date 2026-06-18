<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/swab.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/swab.h

Purpose: Selects PowerPC byte-swap implementation details for UAPI consumers.

Important APIs/types/functions: Defines `__SWAB_64_THRU_32__` for GCC on non-ppc64, then relies on generic swab handling.

Control flow: Compile-time macro choice tells generic swab code to implement 64-bit byte swaps through 32-bit operations on PPC32.

State and persistence: No runtime state.

Dependencies and integration points: Depends on Linux types/compiler headers and generic swab machinery.

Risks: Incorrect macro selection can produce inefficient or wrong 64-bit byte swaps on 32-bit builds.

Test signals: Headers compile and byte-swap unit checks for ppc32/ppc64 with GCC-compatible compilers.

Source read size: 24 lines, 602 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/swab.h -->
