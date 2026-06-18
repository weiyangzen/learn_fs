## sources/distributed-fs/ceph-client/arch/s390/include/asm/runtime_instr.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/runtime_instr.h` is a runtime-
instrumentation task state in the s390 ceph-client Linux source snapshot. It has 28 lines and 634
bytes; exported UAPI contract: no.

### Important APIs, Types, And Functions
the UAPI runtime-instruction control block plus task save/restore hooks that preserve
instrumentation state across scheduling and task teardown
Important macros/constants: `_RUNTIME_INSTR_H`.
Important types/layouts: `runtime_instr_cb`, `task_struct`.
Important declarations or inline helpers: `if`, `runtime_instr_release`, `save_ri_cb`, `restore_ri_cb`.

### Control Flow
Control flow is inlined into callers. The header selects the appropriate architecture-specific
helper, executes any embedded instruction sequence or simple predicate, and returns normalized C
values to generic kernel code.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
scheduler, ptrace/perf-style runtime-instrumentation users, and the low-level load/store runtime
instrumentation instructions. Direct include dependencies detected here: `uapi/asm/runtime_instr.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for scheduler, ptrace/perf-style runtime-
instrumentation users, and the low-level load/store runtime instrumentation instructions. For UAPI
files, the integration point also includes headers_install and userspace programs compiled against
the exported layout.

### Risks
incorrect save/restore can leak instrumentation controls between tasks or leave hardware runtime
tracing enabled after release

### Test Signals
runtime-instrumentation enable/disable tests, context-switch stress, and task-exit cleanup paths
