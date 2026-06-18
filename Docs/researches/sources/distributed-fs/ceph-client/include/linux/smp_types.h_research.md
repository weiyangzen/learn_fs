<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/smp_types.h -->
# sources/distributed-fs/ceph-client/include/linux/smp_types.h

## Purpose
`smp_types.h` defines the low-level call-single queue node shared by generic SMP function calls and irq_work-style users. It keeps common flag/type layout separate from the higher-level SMP API.

## Important APIs, Types, and Functions
The anonymous enum defines low bits for `CSD_FLAG_LOCK`, irq-work flags (`IRQ_WORK_PENDING`, `IRQ_WORK_BUSY`, `IRQ_WORK_LAZY`, `IRQ_WORK_HARD_IRQ`, `IRQ_WORK_CLAIMED`), and high-nibble node types (`CSD_TYPE_ASYNC`, `CSD_TYPE_SYNC`, `CSD_TYPE_IRQ_WORK`, `CSD_TYPE_TTWU`, `CSD_FLAG_TYPE_MASK`). `struct __call_single_node` contains an `llist_node`, a union of `u_flags` and `a_flags`, and optional `src`/`dst` CPU fields on 64-bit builds.

## Control Flow
There is no executable flow here. The comments document how `flush_smp_call_function_queue()` first reads the type from `u_flags`, then interprets the memory following the node as either call-single data, irq_work, or TTWU queue data. The shared first-field layout lets heterogeneous work items coexist on the same per-CPU llist queue.

## State and Persistence Behavior
State is transient per queued cross-CPU work item. `u_flags` or `a_flags` records pending/busy/lock/type state until the target CPU consumes the node. Optional `src`/`dst` fields support debugging or tracing on 64-bit systems. There is no persistent storage.

## Dependencies and Integration Points
The header depends on `linux/llist.h` and is consumed by `smp.h`, generic SMP call-function code, irq_work, scheduler wakeup pathways, and any code that embeds `struct __call_single_node` as its queue-compatible prefix.

## Risks and Test Signals
Risks include changing flag values or layout without updating all queue consumers, reading atomic flags through the wrong union member, and misclassifying node type before interpreting the enclosing structure. Test signals include SMP function-call selftests, irq_work tests, scheduler wakeup stress, CSD lock debugging, and build coverage across 32-bit and 64-bit configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/smp_types.h -->
