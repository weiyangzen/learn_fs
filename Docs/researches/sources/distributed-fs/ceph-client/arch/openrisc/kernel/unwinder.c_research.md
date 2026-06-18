<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/unwinder.c -->
# sources/distributed-fs/ceph-client/arch/openrisc/kernel/unwinder.c

## Purpose
Implements OpenRISC stack unwinding with frame-pointer-aware reliable mode and fallback stack scanning.

## Important APIs, Types, And Functions
Under `CONFIG_FRAME_POINTER`, `struct or1k_frameinfo` models previous FP, return address, and previous top. `or1k_frameinfo_valid()` validates frame chain and text address. `unwind_stack()` invokes caller callback for discovered return addresses. Without frame pointers, it scans stack words for kernel text addresses and marks them unreliable.

## Control Flow
Frame-pointer mode scans stack positions and only marks a hit reliable if the next expected frame pointer matches. Fallback mode linearly scans until `kstack_end()`.

## State And Persistence
No persistent state; observes stack memory.

## Dependencies And Integration Points
Used by traps and stacktrace code. Depends on task-stack helpers and kernel text address validation.

## Risks
Frame layout assumptions must match compiler ABI. Fallback mode can report false positives. Reliable stacktrace users may get no entries without frame pointers.

## Test Signals
Frame-pointer builds, Oops call traces, `save_stack_trace*()` consumers, and scheduler-stack filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/kernel/unwinder.c -->
