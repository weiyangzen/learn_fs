# sources/distributed-fs/ceph-client/fs/ntfs/time.h

## Purpose
Defines inline conversion helpers between Linux `timespec64` UTC timestamps and NTFS little-endian 64-bit timestamps measured in 100 ns intervals since 1601-01-01 UTC.

## Important APIs, Types, And Functions
`NTFS_TIME_OFFSET` is the seconds delta between 1601 and 1970. `utc2ntfs()` converts seconds and nanoseconds to 100 ns units and returns `__le64`. `get_current_ntfs_time()` samples coarse real time and converts it. `ntfs2utc()` subtracts the NTFS epoch offset, divides by 10,000,000, and returns `struct timespec64`.

## Control Flow
The helpers are pure inline arithmetic wrappers used by inode and metadata update paths. `ntfs2utc()` uses `div_s64_rem()` to split seconds from 100 ns remainder.

## State And Persistence
No state is stored directly. The converted values become persistent when written into NTFS file-name, standard-information, or volume metadata timestamps by other code.

## Dependencies And Integration Points
Depends on Linux time APIs and endian helpers. The superblock sets `s_time_gran = 100`, matching the 100 ns NTFS granularity represented here.

## Risks And Edge Cases
Negative or pre-1970 NTFS times are supported by signed arithmetic but need callers to tolerate negative `tv_sec`. Conversion truncates nanoseconds to 100 ns units. Very large values depend on 64-bit arithmetic range and caller validation.

## Test Signals
Round-trip known epoch values: NTFS zero, 1601-01-01, 1970-01-01, current time, sub-microsecond truncation, and pre-1970 dates. Verify little-endian encoding on big-endian builds.
