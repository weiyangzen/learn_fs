## sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso.h` is a s390 vDSO metadata in the
s390 ceph-client Linux source snapshot. It has 17 lines and 291 bytes; exported UAPI contract: no.

### Important APIs, Types, And Functions
page count/version constants and getcpu initialization declaration
Important macros/constants: `__S390_VDSO_H__`, `__VDSO_PAGES`, `VDSO_VERSION_STRING`.
Important types/layouts: none detected.
Important declarations or inline helpers: `vdso_getcpu_init`.

### Control Flow
The header itself has no standalone runtime loop; control flow is owned by the implementation files
that include it and call the declared entry points.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
vDSO mapping, datapage layout, getcpu, and userspace time functions. Direct include dependencies
detected here: `vdso/datapage.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for vDSO mapping, datapage layout, getcpu, and
userspace time functions. For UAPI files, the integration point also includes headers_install and
userspace programs compiled against the exported layout.

### Risks
page-count/version mismatch can map incomplete vDSO images

### Test Signals
vdso selftests and process exec/mmap inspection
