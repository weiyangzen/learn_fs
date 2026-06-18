<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/include/libvfio/assert.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/include/libvfio/assert.h

## Purpose
Assertion and ioctl helper macros for VFIO selftests that log observed values and exit with KSFT_FAIL.

## Important APIs, Types, and Functions
VFIO_ASSERT_OP/EQ/NE/LT/LE/GT/GE/TRUE/FALSE/NULL/NOT_NULL, VFIO_FAIL, ioctl_assert.

## Control Flow
Macros evaluate operands once, compare, print file/line/expression/errno, and terminate on failure; ioctl_assert wraps expected-zero ioctl calls.

## State and Persistence
No persistent state; exits process on failure.

## Dependencies and Integration Points
Depends on errno, strerror, stdio, ioctl, and kselftest.h.

## Risks and Edge Cases
Fatal-exit style is unsuitable for recoverable checks; observed values are cast to u64 which may not format all pointer/types ideally.

## Test Signals
Failures produce detailed stderr and KSFT_FAIL exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/vfio/lib/include/libvfio/assert.h -->
