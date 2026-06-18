# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/common.c

## Purpose
This file provides common backing-file setup and teardown for ublk targets that map block I/O onto regular files or block devices.

## Important APIs, Types, and Functions
`backing_file_tgt_init()` opens target backing files with `O_RDWR` and optional `O_DIRECT`, determines size via `fstat()` or `ioctl(BLKGETSIZE64)`, stores file descriptors in `dev->fds`, and records sizes. `backing_file_tgt_deinit()` fsyncs and closes backing file descriptors.

## Control Flow
Initialization asserts that only the ublk char device fd is registered, then iterates configured files. Regular files use `st_size`; block devices use `BLKGETSIZE64`; other file types fail. Teardown fsyncs/closes all backing fds from index 1 onward.

## State and Persistence
It opens and stores file descriptors in `struct ublk_dev`, and writes final data to backing files via fsync during teardown. File contents are persistent because target I/O uses these descriptors.

## Dependencies and Integration Points
It depends on `kublk.h`, Linux block ioctl definitions, and target initialization in `file_backed.c` and `stripe.c`.

## Risks
Partial initialization failures can leave earlier opened fds for caller cleanup. `O_DIRECT` requirements depend on filesystem alignment and target I/O buffer alignment.

## Test Signals
Successful target startup using loop or stripe backends indicates backing files were opened, sized, and registered correctly.
