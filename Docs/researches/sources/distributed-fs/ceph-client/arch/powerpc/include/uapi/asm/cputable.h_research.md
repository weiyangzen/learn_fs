<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/cputable.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/cputable.h

Purpose: Defines PowerPC hardware capability bits reported through `AT_HWCAP` and `AT_HWCAP2`.

Important APIs/types/functions: `PPC_FEATURE_*` bits for 32/64-bit, FPU, Altivec, MMU, SPE, architecture generations, endian features, and `PPC_FEATURE2_*` bits for ISA 2.07 through 3.1, HTM, DSCR, EBB, vector crypto, DARN, SCV, MMA, and related features.

Control flow: Kernel CPU probing builds HWCAP masks; ELF exec exposes them in auxv; libc and applications branch on bits for optimized or required instruction use.

State and persistence: Per-process auxv state mirrors CPU/platform feature state.

Dependencies and integration points: Integrated with CPU feature discovery, OPAL/skiboot device-tree bindings, ELF auxvec setup, glibc, JITs, and optimized libraries.

Risks: Bit values are ABI-stable and coordinated with firmware bindings. Reusing reserved bits or misreporting features can cause illegal instruction faults.

Test signals: Auxv HWCAP inspection across CPU generations, userspace instruction dispatch tests, and CPU feature table build coverage.

Source read size: 63 lines, 2399 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/cputable.h -->
