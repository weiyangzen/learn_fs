## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/stat.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/stat.h` is a s390 stat structure ABI
in the s390 ceph-client Linux source snapshot. It has 34 lines and 809 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
struct stat layout with nanosecond timestamp support
Important macros/constants: `_S390_STAT_H`, `STAT_HAVE_NSEC`.
Important types/layouts: `stat`.
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
stat/fstat/lstat syscalls, libc, and filesystem tooling. Direct include dependencies detected here:
none detected.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for stat/fstat/lstat syscalls, libc, and
filesystem tooling. For UAPI files, the integration point also includes headers_install and
userspace programs compiled against the exported layout.

### Risks
field alignment drift breaks file metadata reads

### Test Signals
stat syscall ABI tests and 31/64-bit userspace checks
