## sources/distributed-fs/ceph-client/arch/s390/include/asm/signal.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/signal.h` is a kernel signal integration
in the s390 ceph-client Linux source snapshot. It has 26 lines and 644 bytes; exported UAPI
contract: no.

### Important APIs, Types, And Functions
s390 signal constants and SA_RESTORER exposure that bridge UAPI signal frames to generic signal code
Important macros/constants: `_ASMS390_SIGNAL_H`, `_NSIG`, `_NSIG_BPW`, `_NSIG_WORDS`, `__ARCH_HAS_SA_RESTORER`.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
uapi signal.h, sigcontext, syscall restart, and vdso/restorer paths. Direct include dependencies
detected here: `uapi/asm/signal.h`, `asm/sigcontext.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for uapi signal.h, sigcontext, syscall restart,
and vdso/restorer paths. For UAPI files, the integration point also includes headers_install and
userspace programs compiled against the exported layout.

### Risks
signal frame ABI mismatches break old userspace and compat signal delivery

### Test Signals
sigaltstack, rt-signal, ptrace signal injection, and compat tests
