<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cpu.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/cpu.h

**Purpose:** Defines MIPS PRId/FPU ID encodings, CPU type enum, ISA level flags, CPU option bits, and ASE bits.

**Important APIs/types/functions:** Includes company IDs, implementation IDs for legacy/MIPS/Broadcom/Cavium/Ingenic/Netlogic/Loongson and others, revision constants, `enum cpu_type_enum`, `MIPS_CPU_ISA_*`, `MIPS_CPU_*` option flags, and `MIPS_ASE_*`.

**Control flow:** Header constants are consumed by CPU probe and feature macros.

**State, dependencies, integration:** Provides the stable numeric vocabulary for CPU detection, errata checks, feature probing, `/proc/cpuinfo`, and module matching.

**Risks and test signals:** Wrong PRId constants misidentify CPUs and select wrong workarounds. Test CPU probe tables against hardware/QEMU PRId values and feature bit assignment uniqueness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cpu.h -->
