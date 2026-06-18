## sources/distributed-fs/ceph-client/arch/s390/include/asm/syscall_wrapper.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/syscall_wrapper.h` is a s390 syscall entry
wrappers in the s390 ceph-client Linux source snapshot. It has 49 lines and 1741 bytes; exported
UAPI contract: no.

### Important APIs, Types, And Functions
macros that translate pt_regs into typed syscall arguments and create s390x/s390 compat syscall
stubs
Important macros/constants: `_ASM_S390_SYSCALL_WRAPPER_H`, `SC_S390_REGS_TO_ARGS(x, ...)`, `SYSCALL_DEFINE0(sname)`, `COND_SYSCALL(name)`, `__S390_SYS_STUBx(x, fullname, name, ...)`, `__SYSCALL_DEFINEx(x, name, ...)`.
Important types/layouts: `pt_regs`.
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
generated syscall tables, asmlinkage entry code, compat ABI, and generic SYSCALL_DEFINE macros.
Direct include dependencies detected here: none detected.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for generated syscall tables, asmlinkage entry
code, compat ABI, and generic SYSCALL_DEFINE macros. For UAPI files, the integration point also
includes headers_install and userspace programs compiled against the exported layout.

### Risks
argument order/sign-extension mistakes surface as ABI corruption under tracing and compat

### Test Signals
syscall ABI tests, compat userland, and build coverage for conditional syscalls
