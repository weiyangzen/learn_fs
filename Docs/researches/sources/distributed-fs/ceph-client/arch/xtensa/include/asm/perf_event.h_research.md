<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/perf_event.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/perf_event.h

## Purpose
Placeholder architecture perf-event header for Xtensa.

## Important APIs, Types, And Functions
Defines only the include guard.

## Control Flow
No control flow.

## State And Persistence
No state.

## Dependencies And Integration Points
Satisfies generic perf includes while platform-specific perf support is handled elsewhere or through Kconfig feature gates.

## Risks And Edge Cases
Generic perf code that expects arch-specific declarations would require this header to grow. Empty content is acceptable only while no such contract is needed.

## Test Signals
Build `CONFIG_PERF_EVENTS` Xtensa variants, especially custom variants with performance monitor support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/perf_event.h -->
