## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/statfs.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/statfs.h` is a s390 statfs ABI in the
s390 ceph-client Linux source snapshot. It has 51 lines and 1058 bytes; exported UAPI contract: yes.

### Important APIs, Types, And Functions
statfs/statfs64 layout for filesystem statistics
Important macros/constants: `_S390_STATFS_H`.
Important types/layouts: `statfs`, `statfs64`.
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
statfs syscalls, libc, and filesystem utilities. Direct include dependencies detected here:
`linux/types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for statfs syscalls, libc, and filesystem
utilities. For UAPI files, the integration point also includes headers_install and userspace
programs compiled against the exported layout.

### Risks
padding or type-size drift breaks filesystem capacity reporting

### Test Signals
statfs syscall ABI tests across filesystems
