# sources/distributed-fs/lizardfs/src/master/quota_database.cc

## Purpose

`quota_database.cc` implements `QuotaDatabase` operations that are not inline in the header: removing quotas, testing quota exceedance, enumerating entries, and computing a checksum. The source was read as a complete 123-line implementation.

## Important APIs, Types, and Functions

Methods implemented are `remove(owner_type, owner_id, rigor, resource)`, `remove(owner_type, owner_id)`, `exceeds`, `getEntries`, `getEntriesWithStats`, and `checksum`. They operate on `quota_data_`, a per-owner-type map from owner ID to a `Limits` array indexed by `QuotaRigor` and `QuotaResource`.

## Control Flow

Remove finds the owner map entry, clears a single resource or erases the whole owner, and erases empty all-zero limit arrays. `exceeds` returns false for missing entries, then checks each proposed resource delta against the selected soft/hard limit plus current used value. Enumeration walks user/group/inode owner types and soft/hard resources, optionally emitting used stats only for resources with a nonzero soft/hard limit. Checksum folds only nonzero soft/hard limits into a deterministic seed.

## State and Persistence Behavior

State is in-memory quota limits and usage counters. Usage (`QuotaRigor::kUsed`) participates in exceedance and stats enumeration but is intentionally excluded from `checksum`, so metadata checksums represent quota limits, not live usage.

## Dependencies and Integration Points

It depends on `protocol/quota.h`, hash helpers, and checksum combination helpers. Filesystem quota code updates usage and consults exceedance during operations such as snapshots and creation.

## Risks and Edge Cases

`update` in the header adds signed deltas into unsigned counters without local underflow checks. `exceeds` adds an `int64_t` delta to `uint64_t` usage, so negative deltas require caller discipline. Zero limits mean no limit. `getEntriesWithStats` omits used-only entries when no soft/hard limit exists for that resource.

## Test Signals

Quota unit tests cover set/get/remove, exceedance boundaries, corner cases, and checksum invariance to usage. Additional useful tests would include negative updates, all owner types, and stats enumeration ordering expectations.
