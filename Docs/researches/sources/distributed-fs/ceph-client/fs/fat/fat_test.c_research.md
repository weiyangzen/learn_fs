# sources/distributed-fs/ceph-client/fs/fat/fat_test.c

## Purpose
`fat_test.c` is a KUnit suite for small deterministic FAT helpers, mainly short-name checksum and timestamp conversion/truncation behavior. It gives direct regression coverage for date range clamping, timezone offsets, leap-year handling, VFAT centisecond fields, and FAT atime granularity.

## Important APIs, Types, and Functions
- `fat_checksum_test()` validates the VFAT alias checksum helper for representative 8.3 names.
- `struct fat_timestamp_testcase`, `struct fat_unix2fat_clamp_testcase`, and `struct fat_truncate_atime_testcase` define parameterized time cases.
- `fat_test_set_time_offset()` initializes a fake `msdos_sb_info` with controlled timestamp offset policy.
- `fat_time_fat2unix_test()`, `fat_time_unix2fat_test()`, `fat_time_unix2fat_clamp_test()`, `fat_time_unix2fat_no_csec_test()`, and `fat_truncate_atime_test()` exercise exported helpers from `misc.c`.
- `kunit_test_suites(&fat_test_suite)` registers the suite as `fat_test`.

## Control Flow
The suite builds static parameter arrays, exposes them through `KUNIT_ARRAY_PARAM`, and runs each helper against one testcase at a time. Each test prepares a fake superblock info object, calls the conversion function, and checks exact seconds, nanoseconds, date, time, or centisecond outputs.

## State and Persistence
No filesystem state is persisted. The tests intentionally avoid mounting a FAT image and instead isolate pure conversion logic using in-memory `msdos_sb_info` values. This makes the suite fast and deterministic but limits coverage to helper-level behavior.

## Dependencies and Integration Points
The tests include `fat.h` and rely on `fat_time_fat2unix()`, `fat_time_unix2fat()`, and `fat_truncate_atime()` being exported for test access. The covered helpers are used by inode fill/writeback, directory creation, setattr, and timestamp update paths throughout the FAT implementation.

## Risks and Test Signals
The test data targets high-risk time semantics: earliest FAT date, latest FAT date, 2100 non-leap behavior, timezone offsets that cross FAT range boundaries, odd-second VFAT resolution, 10 ms centiseconds, and atime truncation to local midnight. Gaps remain around directory slot parsing, cluster allocation, cache invalidation, mount parsing, and NLS name conversion.
