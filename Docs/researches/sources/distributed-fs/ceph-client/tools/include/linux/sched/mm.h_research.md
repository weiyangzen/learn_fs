<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/sched/mm.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/sched/mm.h

## Purpose
`sched/mm.h` provides the single allocation-context annotation needed by tools code.

## APIs And Flow
It defines `might_alloc(gfp)` as a no-op statement macro. No scheduler or mm lifetime functions are present.

## State, Dependencies, Risks, Tests
There is no state or dependency. Integration is with allocator paths that retain kernel debug annotations while building in user space. Risks are losing might-sleep or reclaim-context diagnostics and assuming this header provides real `mm_struct` helpers. Test signal is compilation of allocator code with `might_alloc()` calls and separate checks that real mm APIs are not required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/sched/mm.h -->
