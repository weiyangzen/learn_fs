<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/auxvec.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/auxvec.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/auxvec.h` defines arm64 auxiliary-vector entries for the vDSO base and minimum signal stack size. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `__ASM_AUXVEC_H`, `AT_SYSINFO_EHDR`, `AT_MINSIGSTKSZ`, `AT_VECTOR_SIZE_ARCH`. The file is 26 lines / 912 bytes. There are no direct C include dependencies in this file.

### Control Flow
ELF exec code emits these constants into each new process auxv so libc can find the vDSO and size signal stacks.

### State, Persistence, And Dependencies
The values persist per process in the initial userspace auxiliary vector. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Wrong auxv numbering breaks libc vDSO discovery or signal-stack sizing.

### Test Signals
Run exec/auxv selftests and inspect `/proc/self/auxv` for `AT_SYSINFO_EHDR` and `AT_MINSIGSTKSZ`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/auxvec.h -->
