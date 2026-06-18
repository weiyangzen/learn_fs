## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/chpid.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/chpid.h` is a channel-path identifier
ABI in the s390 ceph-client Linux source snapshot. It has 23 lines and 456 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
chp_id layout and maximum channel-path id constant shared with channel-subsystem ioctls
Important macros/constants: `_UAPI_ASM_S390_CHPID_H`, `__MAX_CHPID`.
Important types/layouts: `chp_id`.
Important declarations or inline helpers: none detected.

### Control Flow
There is no executable control flow in this header; it defines constants and structure layouts that
are consumed by syscall, ioctl, signal, ptrace, or library paths elsewhere.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
CHSC, SCLP, cio tooling, and userspace channel path management. Direct include dependencies detected
here: `linux/string.h`, `linux/types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for CHSC, SCLP, cio tooling, and userspace
channel path management. For UAPI files, the integration point also includes headers_install and
userspace programs compiled against the exported layout.

### Risks
layout changes break management tools and kernel/user ioctl copies

### Test Signals
CHSC userspace tools and ioctl ABI checks
