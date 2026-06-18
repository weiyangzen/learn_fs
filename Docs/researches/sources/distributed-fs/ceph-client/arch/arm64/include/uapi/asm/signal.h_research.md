<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/signal.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/signal.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/signal.h` sets arm64 signal ABI constants for `SA_RESTORER`, minimum signal stack size, and default signal stack size before including generic signal definitions. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `__ASM_SIGNAL_H`, `SA_RESTORER`, `MINSIGSTKSZ`, `SIGSTKSZ`. The file is 28 lines / 898 bytes. Direct includes are `asm-generic/signal.h`.

### Control Flow
Signal setup and libc signal APIs use these constants when installing handlers and allocating alternate stacks.

### State, Persistence, And Dependencies
Signal stack choices persist in per-task signal state after `sigaltstack`. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Too-small stack constants can overflow with SVE/SME signal records; flag drift breaks handler installation ABI.

### Test Signals
Run signal-stack selftests with large vector states and libc signal API compile checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/signal.h -->
