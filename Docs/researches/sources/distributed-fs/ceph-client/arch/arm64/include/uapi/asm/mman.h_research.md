<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/mman.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/mman.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/mman.h` adds arm64 memory-protection flags for BTI and MTE plus execute/read pkey mask values before including generic mmap definitions. It belongs to the arm64 Linux-kernel compatibility code imported under the Ceph client source tree, so Ceph depends on it indirectly through the kernel facilities that make networking, memory management, page cache, and filesystem execution work on arm64.

### Important APIs, Types, And Functions
macros: `_UAPI__ASM_MMAN_H`, `PROT_BTI`, `PROT_MTE`, `PKEY_DISABLE_EXECUTE`, `PKEY_DISABLE_READ`, `PKEY_ACCESS_MASK`. The file is 19 lines / 552 bytes. Direct includes are `asm-generic/mman.h`.

### Control Flow
Userspace passes these flags to `mmap`, `mprotect`, and pkey APIs; MM code validates and applies BTI/MTE permissions to VMAs.

### State, Persistence, And Dependencies
Flags persist in VMA permissions and page-table attributes. Integration dependencies include generic Linux arm64 architecture code, Kbuild/UAPI generation where applicable, and any included subsystem headers listed above.

### Integration Points
This file integrates with arm64 architecture boot, exception, syscall, virtualization, vDSO, ACPI, Xen, MM, or UAPI consumers according to its exported surface. In this Ceph client source snapshot, the integration is architectural rather than Ceph-protocol-specific: the distributed filesystem client relies on these contracts for safe user copies, syscall ABI stability, vDSO time, CPU feature handling, virtualization, ACPI boot, and compat execution on arm64 systems.

### Risks
Wrong values or masks break BTI landing-pad enforcement, MTE tag checking, or pkey permission semantics.

### Test Signals
Run `mmap`/`mprotect`, BTI, MTE, and pkey selftests on supporting hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/uapi/asm/mman.h -->
