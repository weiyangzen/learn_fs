<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/bitsperlong.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/bitsperlong.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/bitsperlong.h` sets arm64 UAPI `__BITS_PER_LONG` to 64 for native userspace and then includes the generic definition fallback. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `__ASM_BITSPERLONG_H`, `__BITS_PER_LONG`. The file is 29 lines / 960 bytes. Direct includes are `asm-generic/bitsperlong.h`.

### Control Flow
Userspace and sanitized kernel headers consume this compile-time constant when sizing long-based ABI structures.

### State, Persistence, And Dependencies
No runtime state; it is a C ABI sizing contract. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
A wrong value changes structure layouts and ioctl ABI on native arm64.

### Test Signals
Build native and compat UAPI consumers and run ABI layout checks for long-sized structs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/bitsperlong.h -->
