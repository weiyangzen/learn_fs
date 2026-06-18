<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/bmips-spaces.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/bmips-spaces.h

**Purpose:** Overrides fixed-address top placement for BMIPS3300 systems.

**Important APIs/types/functions:** Defines `FIXADDR_TOP` as `0xff000000` to avoid collisions with the BMIPS system base register region.

**Control flow:** Compile-time address-layout override only.

**State, dependencies, integration:** Included by MIPS virtual address layout code for BMIPS configurations.

**Risks and test signals:** Wrong fixed mapping placement can overlap hardware regions. Test BMIPS3300 boot, fixmap users, and highmem/vmalloc layout sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/bmips-spaces.h -->
