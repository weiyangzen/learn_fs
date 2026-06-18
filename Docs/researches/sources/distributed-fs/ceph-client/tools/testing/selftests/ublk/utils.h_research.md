<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/utils.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/utils.h

## Purpose
Small C utility header for ublk selftest support: generic macros, CPU-set allocator, log/debug helpers, and assertion wrapper.

## Important APIs, Types, and Functions
ARRAY_SIZE, offsetof, container_of, round_up, struct allocator, allocator_init/get/put/get_val/deinit, ilog2, ublk_err/log/dbg/assert.

## Control Flow
Inline helpers allocate a CPU_ALLOC bitmap, scan for free integer slots, set/clear bits, and provide conditional stdout/stderr logging controlled by ublk_dbg_mask.

## State and Persistence
Allocator state is the CPU bitmap plus size in caller-owned struct allocator; logging reads global ublk_dbg_mask.

## Dependencies and Integration Points
Depends on glibc CPU_ALLOC APIs, errno, stdio/varargs/assert includes from users, and an external ublk_dbg_mask definition.

## Risks and Edge Cases
No locking, so allocator is not thread-safe; macros evaluate arguments directly and should be used with side-effect caution.

## Test Signals
Compile-time integration and assertion/log behavior in ublk C tools are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/utils.h -->
