# File Research: sources/cow-pools/bcachefs/fs/bcachefs/alloc/replicas.h

Public replicas API and iteration helpers.

Exports:
- Replica sorting, text, validation, and CPU text functions.
- Conversion from bkey or device list to replica entry.
- Replica mark/query functions.
- Cached-data one-device replica initializer.
- Read/write availability checks.
- Superblock and live device data-presence queries.
- Journal replica ref get/put APIs.
- Replica entry kill and GC functions.
- Superblock-to-CPU conversion and superblock field ops.
- Cleanup and leak verification.

Inline helpers:
- `bch2_replicas_entry_has_dev()`
- `bch2_replicas_entry_eq()`
- `replicas_entry_next()`
- `for_each_replicas_entry()`

Role:
- Shared by allocation/accounting, journal, mount/device validation, fsck, and superblock parsing paths.
