## sources/distributed-fs/ceph-client/arch/s390/include/asm/user.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/user.h` is a legacy core-dump user layout
in the s390 ceph-client Linux source snapshot. It has 71 lines and 3237 bytes; exported UAPI
contract: no.

### Important APIs, Types, And Functions
struct user and register aliases used by ptrace/core-dump compatibility interfaces
Important macros/constants: `_S390_USER_H`.
Important types/layouts: `to`, `that`, `pt_regs`, `user`, `user_regs_struct`.
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
ptrace, ELF core dumping, GDB expectations, and UAPI ptrace registers. Direct include dependencies
detected here: `asm/page.h`, `asm/ptrace.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for ptrace, ELF core dumping, GDB expectations,
and UAPI ptrace registers. For UAPI files, the integration point also includes headers_install and
userspace programs compiled against the exported layout.

### Risks
legacy layout changes can break debuggers and crash dump tooling

### Test Signals
ptrace register tests and GDB/core dump inspection
