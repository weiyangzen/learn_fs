# sources/distributed-fs/ceph-client/fs/udf/udftime.c

## Purpose
`udftime.c` converts between UDF disk timestamps and Linux `timespec64`, including UDF timezone encoding and sub-second fields.

## Important APIs, types, and functions
The public functions are `udf_disk_stamp_to_time` and `udf_time_to_disk_stamp`. They operate on ECMA/UDF `struct timestamp` and Linux `struct timespec64`.

## Control flow
Disk-to-Linux conversion checks timestamp type 1 for signed timezone offset in minutes, treats the unspecified `-2047` offset as UTC/no offset, converts calendar fields with `mktime64`, subtracts the offset, and sanitizes sub-second fields by accepting only centiseconds, hundreds-of-microseconds, and microseconds below 100. Linux-to-disk conversion uses `sys_tz.tz_minuteswest`, writes type 1 plus 12-bit offset, converts adjusted seconds through `time64_to_tm`, and splits nanoseconds into UDF sub-second components.

## State and persistence
The file has no private state. It affects persistent recording, inode, and LVID timestamps and the runtime interpretation of media timestamps.

## Dependencies and integration points
It depends on kernel time conversion helpers and is declared through `udfdecl.h`. `super.c` uses it for PVD recording time and LVID open/close timestamps; inode code uses it for file timestamps.

## Risks and test signals
Risks include invalid calendar fields, timezone sign errors, unspecified offset interpretation, no leap-second handling, and lossy nanosecond conversion. Test signals include timestamps with explicit positive/negative offsets, unspecified offsets, bogus sub-second fields, pre-1970 or far-future years supported by `time64`, and LVID close timestamp updates.
