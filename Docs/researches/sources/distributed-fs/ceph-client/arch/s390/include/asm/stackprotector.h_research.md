## sources/distributed-fs/ceph-client/arch/s390/include/asm/stackprotector.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/stackprotector.h` is a stack canary
initialization in the s390 ceph-client Linux source snapshot. It has 16 lines and 389 bytes;
exported UAPI contract: no.

### Important APIs, Types, And Functions
boot_init_stack_canary() copies the per-task canary into lowcore for stack protector checks
Important macros/constants: `_ASM_S390_STACKPROTECTOR_H`.
Important types/layouts: none detected.
Important declarations or inline helpers: `boot_init_stack_canary`.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
scheduler current task, lowcore, compiler stack-protector instrumentation, and fork/exec paths.
Direct include dependencies detected here: `linux/sched.h`, `asm/current.h`, `asm/lowcore.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for scheduler current task, lowcore, compiler
stack-protector instrumentation, and fork/exec paths. For UAPI files, the integration point also
includes headers_install and userspace programs compiled against the exported layout.

### Risks
stale canary values reduce stack-smash detection or cause false positives

### Test Signals
stack protector boot coverage and task-switch canary tests
