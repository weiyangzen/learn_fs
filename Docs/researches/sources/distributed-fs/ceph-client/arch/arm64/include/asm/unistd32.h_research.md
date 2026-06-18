<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/unistd32.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/unistd32.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/unistd32.h` adapts the arm64 compat include path so the AArch32 `unistd_32.h` numbers are visible while preserving the historical ARM UAPI include guard name. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `_UAPI__ASM_ARM_UNISTD_H`, `__NR_sync_file_range2`. The file is 9 lines / 240 bytes. Direct includes are `asm/unistd_32.h`.

### Control Flow
The file is purely preprocessor glue. It defines the guard expected by included ARM headers and includes `asm/unistd_32.h`.

### State, Persistence, And Dependencies
No runtime state; the persistent contract is the 32-bit syscall ABI exposed to compat tasks. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Incorrect guard or include ordering can hide generated 32-bit syscall numbers or redefine symbols differently from ARM userspace expectations.

### Test Signals
Build compat syscall users, compare generated `__NR_*` values, and run AArch32 syscall selftests on an arm64 kernel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/unistd32.h -->
