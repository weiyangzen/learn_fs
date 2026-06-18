## sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso-symbols.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/vdso-symbols.h` is a vDSO symbol offset
helper in the s390 ceph-client Linux source snapshot. It has 9 lines and 264 bytes; exported UAPI
contract: no.

### Important APIs, Types, And Functions
VDSO_SYMBOL macro mapping generated offsets into task mm context fields
Important macros/constants: `__S390_VDSO_SYMBOLS_H__`, `VDSO_SYMBOL(tsk, name)`.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.

### Control Flow
The header itself has no standalone runtime loop; control flow is owned by the implementation files
that include it and call the declared entry points.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
vDSO build, generated offsets, exec mapping, and gettimeofday/getcpu users. Direct include
dependencies detected here: `generated/vdso-offsets.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for vDSO build, generated offsets, exec mapping,
and gettimeofday/getcpu users. For UAPI files, the integration point also includes headers_install
and userspace programs compiled against the exported layout.

### Risks
offset drift points userspace vDSO calls at the wrong symbol

### Test Signals
vDSO symbol-offset build checks and vdso selftests
