<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/Kbuild -->
## sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/Kbuild

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/Kbuild` selects generic UAPI headers for arm64 that do not need architecture-specific copies: errno, ioctl, ioctls, and ipcbuf. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
UAPI export directives: `syscall-y += unistd_64.h`, `generic-y += kvm_para.h`. The file is 4 lines / 85 bytes. Dependencies are the generic UAPI headers selected by `generic-y`.

### Control Flow
Kbuild consumes `generic-y` lines while exporting sanitized UAPI headers to userspace.

### State, Persistence, And Dependencies
No runtime state; the output is the installed UAPI header set. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Dropping a generic entry can break userspace header installation or produce missing includes for libc/kernel header consumers.

### Test Signals
Run headers_install, compile UAPI consumers, and compare generated include tree for missing generic headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/Kbuild -->
