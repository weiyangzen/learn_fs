## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/ioctls.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/ioctls.h` is a s390 ioctl additions
in the s390 ceph-client Linux source snapshot. It has 9 lines and 191 bytes; exported UAPI contract:
yes.

### Important APIs, Types, And Functions
FIOQSIZE definition layered on generic ioctl numbers
Important macros/constants: `__ARCH_S390_IOCTLS_H__`, `FIOQSIZE`.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.

### Control Flow
There is no in-kernel execution flow in this exported header. Runtime flow occurs when userspace
fills these stable structures and passes ioctl request numbers to the matching s390 driver, which
copies the data through uaccess and interprets the packed fields exactly as declared here.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
terminal/file ioctl users and generic asm-generic/ioctls.h inclusion. Direct include dependencies
detected here: `asm-generic/ioctls.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for terminal/file ioctl users and generic
asm-generic/ioctls.h inclusion. For UAPI files, the integration point also includes headers_install
and userspace programs compiled against the exported layout.

### Risks
number collisions can break userspace ioctl dispatch

### Test Signals
headers_install and ioctl-number ABI checks
