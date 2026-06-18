<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/unwinder.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/unwinder.h

## Purpose
Declares the OpenRISC stack unwinding callback API.

## Important APIs, Types, And Functions
`unwind_stack(void *data, unsigned long *stack, void (*trace)(void *data, unsigned long addr, int reliable))` scans a kernel stack and reports return addresses with a reliability flag.

## Control Flow
Callers supply a starting stack pointer and callback. `kernel/unwinder.c` either validates frame-pointer records or scans for text addresses.

## State And Persistence
No state. It observes stack memory and text addresses.

## Dependencies And Integration Points
Used by `traps.c` for crash output and `stacktrace.c` for stack trace collection.

## Risks
Reliability depends on frame pointers. Non-frame-pointer mode can produce false positives and marks entries unreliable.

## Test Signals
Stacktrace selftests with `CONFIG_FRAME_POINTER`, crash dump output, and scheduler-stack filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/unwinder.h -->
