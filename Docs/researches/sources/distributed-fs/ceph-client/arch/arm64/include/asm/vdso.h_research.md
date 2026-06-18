<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/vdso.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/vdso.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/vdso.h` defines arm64 vDSO page count and symbol lookup arithmetic used by kernel code that maps and patches the vDSO image. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `__ASM_VDSO_H`, `__VDSO_PAGES`, `VDSO_SYMBOL`. The file is 24 lines / 470 bytes. Direct includes are `generated/vdso-offsets.h`.

### Control Flow
Runtime code passes generated vDSO offsets through `VDSO_SYMBOL` to locate symbols in the mapped image; this header supplies only the compile-time arithmetic.

### State, Persistence, And Dependencies
No storage is created here. It depends on generated `vdso-offsets.h` and the kernel's vDSO mapping data. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Mismatch between generated offsets, page count, and the linked vDSO image can break userspace fast time or signal trampoline entry.

### Test Signals
Build vDSO, run `readelf`/symbol offset checks, and execute vDSO clock/getcpu/selftests on arm64.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/vdso.h -->
