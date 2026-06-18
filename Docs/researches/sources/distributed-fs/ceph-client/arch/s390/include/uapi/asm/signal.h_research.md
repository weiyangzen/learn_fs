## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/signal.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/signal.h` is a s390 signal userspace
ABI in the s390 ceph-client Linux source snapshot. It has 115 lines and 3058 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
signal numbers, sigaction/old_sigaction/sigaltstack declarations, mask sizing, and SA_RESTORER
support
Important macros/constants: `_UAPI_ASMS390_SIGNAL_H`, `NSIG`, `SIGHUP`, `SIGINT`, `SIGQUIT`, `SIGILL`, `SIGTRAP`, `SIGABRT`, `SIGIOT`, `SIGBUS`, `SIGFPE`, `SIGKILL`, `SIGUSR1`, `SIGSEGV`, `SIGUSR2`, `SIGPIPE`, `SIGALRM`, `SIGTERM`, `SIGSTKFLT`, `SIGCHLD`; plus 24 more.
Important types/layouts: `siginfo`, `pt_regs`, `old_sigaction`, `sigaction`, `sigaltstack`.
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
glibc signal headers, kernel signal delivery, and compat userland. Direct include dependencies
detected here: `linux/types.h`, `linux/time.h`, `asm-generic/signal-defs.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for glibc signal headers, kernel signal
delivery, and compat userland. For UAPI files, the integration point also includes headers_install
and userspace programs compiled against the exported layout.

### Risks
renumbering or struct layout changes are userspace ABI breaks

### Test Signals
signal selftests, sigaltstack, and old/new sigaction compatibility
