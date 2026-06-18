<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/addrspace.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/addrspace.h

**Purpose:** Defines MIPS virtual address segments and conversion macros between physical, compatibility, CKSEG, KSEG, XKSEG, and XKPHYS addresses.

**Important APIs/types/functions:** Key macros include `KSEGX`, `CPHYSADDR`, `XPHYSADDR`, `CKSEG*ADDR`, `KSEG*ADDR`, `PHYS_TO_XKPHYS`, `PHYS_TO_XKSEG_*`, `XKPHYS_TO_PHYS`, `KDM_TO_PHYS`, and cache mode constants.

**Control flow:** Header-only macro expansion adapts constants for assembler versus C and 32-bit versus 64-bit builds.

**State, dependencies, integration:** Includes generated `spaces.h` and is widely used by MMU, IO, firmware, and board code.

**Risks and test signals:** Incorrect casts can truncate or sign-extend addresses incorrectly, especially in 64-bit compatibility segments. Test macro values in 32/64-bit builds and firmware pointer conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/addrspace.h -->
