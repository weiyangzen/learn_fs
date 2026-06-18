## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/unistd.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/unistd.h` is a s390 syscall header
export in the s390 ceph-client Linux source snapshot. It has 13 lines and 269 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
generated 64-bit syscall numbers and guard for userspace asm/unistd.h
Important macros/constants: `_UAPI_ASM_S390_UNISTD_H_`.
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
libc syscall wrappers, seccomp/audit tooling, and headers_install. Direct include dependencies
detected here: `asm/unistd_64.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for libc syscall wrappers, seccomp/audit
tooling, and headers_install. For UAPI files, the integration point also includes headers_install
and userspace programs compiled against the exported layout.

### Risks
stale generated inclusion breaks syscall numbering

### Test Signals
headers_install, syscall-number comparison, and seccomp user tests
