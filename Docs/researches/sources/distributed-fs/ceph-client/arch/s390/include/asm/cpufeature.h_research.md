<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cpufeature.h -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/cpufeature.h

Purpose: Declares s390 CPU feature IDs and facility-backed convenience predicates.

Important APIs/types/functions: `enum` feature IDs, `cpu_feature()`, `cpu_have_feature()`, and helpers such as `cpu_has_vx()`, `cpu_has_nx()`, `cpu_has_gs()`, `cpu_has_edat*()`, and `cpu_has_topology()`. Source-visible declarations include: #define __ASM_S390_CPUFEATURE_H; enum {; #define cpu_feature(feature) (feature); int cpu_have_feature(unsigned int nr);; #define cpu_has_bear() test_facility(193); #define cpu_has_edat1() test_facility(8); #define cpu_has_edat2() test_facility(78); #define cpu_has_gs() test_facility(133); #define cpu_has_nx() test_facility(130); #define cpu_has_rdp() test_facility(194).

Control flow: Feature users query indexed software features or direct facility bits to select instructions and code paths.

State and persistence behavior: Persistent state is CPU feature/facility discovery data initialized at boot.

Dependencies and integration points: Direct includes are #include <asm/facility.h>. Integrated with Integrates cpufeature core, alternatives, crypto, MM, vector/FPU, and topology code..

Risks: Feature IDs and facility numbers must remain stable; false positives lead to illegal instructions.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 37 lines, 942 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/cpufeature.h -->
