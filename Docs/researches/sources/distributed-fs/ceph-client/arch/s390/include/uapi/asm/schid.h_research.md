## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/schid.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/schid.h` is a subchannel-id userspace
ABI in the s390 ceph-client Linux source snapshot. It has 20 lines and 382 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
subchannel_id bitfield layout shared with CHSC and KVM I/O interrupt APIs
Important macros/constants: `_UAPIASM_SCHID_H`.
Important types/layouts: `subchannel_id`.
Important declarations or inline helpers: none detected.

### Control Flow
There is no executable control flow in this header; it defines constants and structure layouts that
are consumed by syscall, ioctl, signal, ptrace, or library paths elsewhere.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
cio ioctls, userspace channel tooling, and KVM I/O injection. Direct include dependencies detected
here: `linux/types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for cio ioctls, userspace channel tooling,
and KVM I/O injection. For UAPI files, the integration point also includes headers_install and
userspace programs compiled against the exported layout.

### Risks
bitfield drift addresses the wrong channel device

### Test Signals
CHSC/KVM subchannel id encode/decode tests
