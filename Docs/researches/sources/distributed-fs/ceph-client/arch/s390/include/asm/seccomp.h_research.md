## sources/distributed-fs/ceph-client/arch/s390/include/asm/seccomp.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/seccomp.h` is a s390 seccomp syscall
metadata in the s390 ceph-client Linux source snapshot. It has 23 lines and 648 bytes; exported UAPI
contract: no.

### Important APIs, Types, And Functions
native and compat seccomp syscall numbers and AUDIT_ARCH mapping used by generic seccomp filtering
Important macros/constants: `_ASM_S390_SECCOMP_H`, `__NR_seccomp_read`, `__NR_seccomp_write`, `__NR_seccomp_exit`, `__NR_seccomp_sigreturn`, `__NR_seccomp_read_32`, `__NR_seccomp_write_32`, `__NR_seccomp_exit_32`, `__NR_seccomp_sigreturn_32`, `SECCOMP_ARCH_NATIVE`, `SECCOMP_ARCH_NATIVE_NR`, `SECCOMP_ARCH_NATIVE_NAME`.
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
generic seccomp, audit, syscall numbering, and 31-bit compat task handling. Direct include
dependencies detected here: `linux/unistd.h`, `asm-generic/seccomp.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for generic seccomp, audit, syscall numbering,
and 31-bit compat task handling. For UAPI files, the integration point also includes headers_install
and userspace programs compiled against the exported layout.

### Risks
wrong audit arch or compat syscall numbers can allow or block the wrong filtered operations

### Test Signals
seccomp BPF tests on native and compat processes
