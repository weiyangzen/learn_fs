## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/bitsperlong.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/bitsperlong.h` is a userspace word-
size constants in the s390 ceph-client Linux source snapshot. It has 10 lines and 235 bytes;
exported UAPI contract: yes.

### Important APIs, Types, And Functions
__BITS_PER_LONG selection for s390 UAPI with generic fallback inclusion
Important macros/constants: `__ASM_S390_BITSPERLONG_H`, `__BITS_PER_LONG`.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.

### Control Flow
Most content is ABI layout, but the inline helpers issue small architecture instructions or register
moves directly from userspace-visible code. Callers allocate the declared control block, invoke the
helper, and rely on the compiler preserving the documented layout and clobbers.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
userspace ABI type sizing and generic asm headers. Direct include dependencies detected here: `asm-
generic/bitsperlong.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for userspace ABI type sizing and generic
asm headers. For UAPI files, the integration point also includes headers_install and userspace
programs compiled against the exported layout.

### Risks
word-size drift breaks ioctl structure layout on 31/64-bit ABIs

### Test Signals
headers_install and compat userspace compile tests
