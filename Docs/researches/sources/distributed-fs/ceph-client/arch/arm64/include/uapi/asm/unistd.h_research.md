<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/unistd.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/unistd.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/unistd.h` includes generated native arm64 syscall numbers from `asm/unistd_64.h` for the exported UAPI header set. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
no local C symbols beyond include or Kbuild directives. The file is 2 lines / 90 bytes. Direct includes are `asm/unistd_64.h`.

### Control Flow
There is no runtime control flow; headers_install and userspace builds consume the generated syscall constants.

### State, Persistence, And Dependencies
No local state; the stable syscall number ABI is the persistent contract. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Generated syscall header drift breaks libc, seccomp, ptrace, and syscall dispatch tooling.

### Test Signals
Run headers_install, compile syscall users, and compare native arm64 `__NR_*` values against the generated syscall table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/unistd.h -->
