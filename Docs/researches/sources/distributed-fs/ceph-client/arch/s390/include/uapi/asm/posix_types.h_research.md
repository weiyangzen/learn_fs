## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/posix_types.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/posix_types.h` is a s390 POSIX type
ABI in the s390 ceph-client Linux source snapshot. It has 45 lines and 1278 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
kernel typedef overrides for size, dev, uid/gid, ino, mode, and ipc pid before generic POSIX types
Important macros/constants: `__ARCH_S390_POSIX_TYPES_H`, `__kernel_size_t`, `__kernel_old_dev_t`, `__kernel_old_uid_t`, `__kernel_ino_t`, `__kernel_mode_t`, `__kernel_ipc_pid_t`, `__kernel_uid_t`, `__kernel_gid_t`.
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
glibc/musl headers, syscall structures, and compat ABI. Direct include dependencies detected here:
`asm-generic/posix_types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for glibc/musl headers, syscall
structures, and compat ABI. For UAPI files, the integration point also includes headers_install and
userspace programs compiled against the exported layout.

### Risks
type-size changes break stat/ipc/ioctl structures

### Test Signals
headers_install and 31/64-bit userspace ABI checks
