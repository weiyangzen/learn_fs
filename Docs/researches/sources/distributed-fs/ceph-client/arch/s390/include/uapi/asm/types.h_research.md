## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/types.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/types.h` is a s390 exported integer
types in the s390 ceph-client Linux source snapshot. It has 30 lines and 513 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
generic int-ll64 type inclusion for UAPI consumers
Important macros/constants: `_UAPI_S390_TYPES_H`.
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
all exported asm headers and libc/kernel type consistency. Direct include dependencies detected
here: `asm-generic/int-ll64.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for all exported asm headers and
libc/kernel type consistency. For UAPI files, the integration point also includes headers_install
and userspace programs compiled against the exported layout.

### Risks
type model drift breaks ioctl and syscall structures

### Test Signals
headers_install and ABI layout checks
