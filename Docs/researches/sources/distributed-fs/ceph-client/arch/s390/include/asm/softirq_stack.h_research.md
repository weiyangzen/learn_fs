## sources/distributed-fs/ceph-client/arch/s390/include/asm/softirq_stack.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/softirq_stack.h` is a softirq alternate
stack execution in the s390 ceph-client Linux source snapshot. It has 14 lines and 372 bytes;
exported UAPI contract: no.

### Important APIs, Types, And Functions
do_softirq_own_stack() wrapper that switches to the lowcore async stack before running softirq work
Important macros/constants: `__ASM_S390_SOFTIRQ_STACK_H`.
Important types/layouts: none detected.
Important declarations or inline helpers: `do_softirq_own_stack`.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
generic softirq dispatch, lowcore stack fields, and stacktrace classification. Direct include
dependencies detected here: `asm/lowcore.h`, `asm/stacktrace.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for generic softirq dispatch, lowcore stack
fields, and stacktrace classification. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
wrong stack selection can overflow task stacks or confuse unwinding

### Test Signals
network/storage interrupt load with stack overflow and stacktrace diagnostics
