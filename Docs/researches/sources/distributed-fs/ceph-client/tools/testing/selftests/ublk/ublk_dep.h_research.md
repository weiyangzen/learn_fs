<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/ublk_dep.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/ublk_dep.h

## Purpose
Compatibility header that defines newer ublk ioctl/feature constants when the build headers do not provide them.

## Important APIs, Types, and Functions
UBLK_U_IO_REGISTER_IO_BUF, UBLK_U_IO_UNREGISTER_IO_BUF, UBLK_F_USER_RECOVERY_FAIL_IO, UBLK_F_ZONED.

## Control Flow
Pure preprocessor fallback: include guard checks each symbol and defines missing ioctl numbers or feature bits.

## State and Persistence
No runtime state or persistence.

## Dependencies and Integration Points
Depends on struct ublksrv_io_cmd and ioctl encoding macros from surrounding ublk build headers.

## Risks and Edge Cases
Risk is numeric drift if upstream ABI changes; fallback definitions must remain synchronized with kernel UAPI.

## Test Signals
Build success on older headers is the main signal; no direct runtime test in this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/ublk_dep.h -->
