<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cpu-features.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/cpu-features.h

**Purpose:** Converts probed `cpu_data[0]` ISA, ASE, option, cache, and guest fields into feature macros used throughout MIPS code.

**Important APIs/types/functions:** Defines feature predicates such as `cpu_has_tlb`, `cpu_has_fpu`, `cpu_has_llsc`, `cpu_has_mips32r2`, `cpu_has_mips64`, `cpu_has_mmips`, `cpu_has_dc_aliases`, `cpu_has_msa`, `cpu_has_vz`, `cpu_has_mmid`, guest feature predicates, cache line helpers, and many errata/ISA shortcut macros.

**Control flow:** Most macros prefer override definitions from `cpu-feature-overrides.h`, else derive from `cpu_data[0]`, compile-time `MIPS_ISA_REV`, config symbols, or `boot_cpu_type()` switch expressions.

**State, dependencies, integration:** Central dependency for cache, atomics, MMU, FPU, virtualization, SMP, timer, and exception code. Assumes CPU0 options are a superset on SMP.

**Risks and test signals:** Overstating features can emit unsupported instructions; understating features disables needed fast paths. Test CPU probe data against macros on all supported CPU families, override configs, no-FPU boot option, SMP heterogeneous assumptions, and guest dynamic feature paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cpu-features.h -->
