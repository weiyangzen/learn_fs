## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/ucontext.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/ucontext.h` is a s390 ucontext ABI in
the s390 ceph-client Linux source snapshot. It has 41 lines and 1207 bytes; exported UAPI contract:
yes.

### Important APIs, Types, And Functions
ucontext and ucontext_extended layouts with high-GPR and vector-register flags
Important macros/constants: `_ASM_S390_UCONTEXT_H`, `UC_GPRS_HIGH`, `UC_VXRS`.
Important types/layouts: `ucontext_extended`, `ucontext`.
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
signal frames, getcontext/setcontext, libc, and vector-register restore. Direct include dependencies
detected here: none detected.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for signal frames, getcontext/setcontext,
libc, and vector-register restore. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
layout drift corrupts user context switching and signal restore

### Test Signals
libc context tests, signal ucontext inspection, and vector-register cases
