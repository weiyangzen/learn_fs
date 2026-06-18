## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/ipcbuf.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/ipcbuf.h` is a SysV IPC permission
ABI in the s390 ceph-client Linux source snapshot. It has 31 lines and 702 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
ipc64_perm layout with s390-specific padding and type choices
Important macros/constants: `__S390_IPCBUF_H__`.
Important types/layouts: `ipc64_perm`.
Important declarations or inline helpers: none detected.

### Control Flow
There is no executable control flow in this header; it defines constants and structure layouts that
are consumed by syscall, ioctl, signal, ptrace, or library paths elsewhere.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
SysV IPC syscalls, glibc headers, and 31/64-bit ABI compatibility. Direct include dependencies
detected here: `linux/posix_types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for SysV IPC syscalls, glibc headers, and
31/64-bit ABI compatibility. For UAPI files, the integration point also includes headers_install and
userspace programs compiled against the exported layout.

### Risks
layout changes break shm/msg/sem permission queries

### Test Signals
ipc syscall ABI tests and compat userspace checks
