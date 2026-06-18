<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/hwcap.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/hwcap.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/hwcap.h` defines arm64 `AT_HWCAP` and `AT_HWCAP2` feature bits for FP/SIMD, crypto, atomics, SVE/SME, pointer auth, MTE, RNG, and newer architectural extensions. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `_UAPI__ASM_HWCAP_H`, `HWCAP_FP`, `HWCAP_ASIMD`, `HWCAP_EVTSTRM`, `HWCAP_AES`, `HWCAP_PMULL`, `HWCAP_SHA1`, `HWCAP_SHA2`, `HWCAP_CRC32`, `HWCAP_ATOMICS`, `HWCAP_FPHP`, `HWCAP_ASIMDHP`, `HWCAP_CPUID`, `HWCAP_ASIMDRDM`, `HWCAP_JSCVT`, `HWCAP_FCMA`, `HWCAP_LRCPC`, `HWCAP_DCPOP`, `HWCAP_SHA3`, `HWCAP_SM3`, `HWCAP_SM4`, `HWCAP_ASIMDDP`, `HWCAP_SHA512`, `HWCAP_SVE`, `HWCAP_ASIMDFHM`, `HWCAP_DIT`, `HWCAP_USCAT`, `HWCAP_ILRCPC`, and 89 more. The file is 151 lines / 4859 bytes. There are no direct C include dependencies in this file.

### Control Flow
CPU feature detection populates these bitmaps during exec; userspace libraries use them to select optimized code paths.

### State, Persistence, And Dependencies
The capability bits persist per process in auxv and are derived from system-wide CPU feature state. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Advertising unsupported features can crash optimized userspace; omitting supported bits can disable performance paths or feature tests.

### Test Signals
Run cpufeature and hwcap selftests, compare `/proc/cpuinfo`/auxv exposure, and test heterogeneous CPU systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/hwcap.h -->
