<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cpufeature.h -->
## sources/distributed-fs/ceph-client/arch/mips/include/asm/cpufeature.h

**Purpose:** Provides module CPU feature matching helpers based on MIPS ELF hardware capabilities.

**Important APIs/types/functions:** `MAX_CPU_FEATURES`, `cpu_feature(x)` maps an HWCAP name to bit index, and `cpu_have_feature()` tests `elf_hwcap`.

**Control flow:** Header-only bit tests for module loader feature matching.

**State, dependencies, integration:** Depends on UAPI hwcap definitions and `elf_hwcap` from ELF setup.

**Risks and test signals:** HWCAP bit mismatch prevents modules from loading or lets incompatible modules load. Test module_cpu_feature_match users and HWCAP exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/cpufeature.h -->
