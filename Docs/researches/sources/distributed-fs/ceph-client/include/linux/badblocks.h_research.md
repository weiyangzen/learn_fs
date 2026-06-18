# sources/distributed-fs/ceph-client/include/linux/badblocks.h

## Purpose
Declares a compact bad-block extent table used by block-like devices to track damaged sectors, including acknowledged versus unacknowledged bad blocks.

## Important APIs, types, and functions
- `BB_*` masks/macros encode a bad-block extent in a 64-bit entry: 54-bit sector offset, 9-bit length minus one, and one acknowledged bit.
- `MAX_BADBLOCKS` stores one page of 64-bit entries.
- `struct badblocks` contains device association, count, unacknowledged hint, sector shift, extent page, change flag, seqlock, and device range.
- `badblocks_check()`, `badblocks_set()`, `badblocks_clear()`, `ack_all_badblocks()`, `badblocks_show()`, `badblocks_store()`, init/exit, and devm helpers are the main API.

## Control flow and state
Device code initializes the table, sets or clears bad sector ranges, checks I/O ranges against it, and exposes show/store helpers for sysfs-like control. Writers update the sorted table under the seqlock; readers can retry if the sequence changes.

## State and persistence behavior
The in-memory table records extents only for the lifetime of `struct badblocks`; persistence depends on the owning device or metadata layer. `changed` signals dirty metadata to the owner, and `unacked_exist` is a hint that is only cleared after a read finds none.

## Dependencies and integration points
Depends on seqlocks, device warnings, kernel types, and page-size storage. Integrated by md/raid, nvdimm, and other block subsystems that need bad-sector bookkeeping.

## Risks
The table can fill (`MAX_BADBLOCKS`), range encoding is limited to `BB_MAX_LEN`, and shift conversions can disable badblocks if negative. Incorrect use of `devm_exit_badblocks()` on the wrong device emits a warning and leaves cleanup to the correct owner.

## Test signals
Tests should cover set/check/clear overlap cases, acknowledged and unacknowledged states, full-table behavior, sysfs parsing/printing, changed-flag transitions, and concurrent readers during updates.
