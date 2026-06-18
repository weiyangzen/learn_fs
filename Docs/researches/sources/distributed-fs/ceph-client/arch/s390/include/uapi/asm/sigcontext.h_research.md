## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/sigcontext.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/sigcontext.h` is a s390 signal-
context ABI in the s390 ceph-client Linux source snapshot. It has 70 lines and 1432 bytes; exported
UAPI contract: yes.

### Important APIs, Types, And Functions
saved PSW/GPR/ACR/FPR/vector register pointers, signal mask sizing, and frame-size constants
Important macros/constants: `_ASM_S390_SIGCONTEXT_H`, `__NUM_GPRS`, `__NUM_FPRS`, `__NUM_ACRS`, `__NUM_VXRS`, `__NUM_VXRS_LOW`, `__NUM_VXRS_HIGH`, `_SIGCONTEXT_NSIG`, `_SIGCONTEXT_NSIG_BPW`, `__SIGNAL_FRAMESIZE`, `_SIGCONTEXT_NSIG_WORDS`, `_SIGMASK_COPY_SIZE`.
Important types/layouts: `sigcontext`.
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
signal delivery/return, glibc sigcontext, ptrace, and core dumps. Direct include dependencies
detected here: `linux/compiler.h`, `linux/types.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for signal delivery/return, glibc
sigcontext, ptrace, and core dumps. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
layout changes break signal return and debugger signal-frame decoding

### Test Signals
rt-signal selftests, vector-register signal tests, and compat signal frames
