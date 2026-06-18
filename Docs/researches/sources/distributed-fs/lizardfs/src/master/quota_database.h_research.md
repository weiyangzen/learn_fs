# sources/distributed-fs/lizardfs/src/master/quota_database.h

## Purpose

`quota_database.h` declares and partly implements `QuotaDatabase`, an in-memory storage object for quota limits and usage by owner type, owner ID, rigor, and resource. The source was read as a complete 150-line header.

## Important APIs, Types, and Functions

Types include `Limits` (`array<array<uint64_t, 2>, 3>`) and `DataTable` (`unordered_map<uint32_t, Limits>`). Inline methods include `get`, `set`, `update`, `removeEmpty`, `hash`, and templated `forEach`; non-inline methods are declared for remove/exceeds/enumeration/checksum.

## Control Flow

Inline setters create owner entries on demand and write array slots directly. `removeEmpty` erases entries whose entire `Limits` value is zero. `forEach` iterates owner types user/group/inode, then entries, then soft/hard rigor and inode/size resources.

## State and Persistence Behavior

The database stores quota state in memory. Persistence is external through metadata serialization/changelog replay; this header defines the structure that those paths populate and inspect.

## Dependencies and Integration Points

It integrates with `protocol/quota.h` types, filesystem quota enforcement, restore `SETQUOTA` application, metadata checksum computation, and tests. `common/hashfn.h` supplies hash combination.

## Risks and Edge Cases

The array layout depends on enum integer values. Direct `update` has no validation for underflow/overflow. `forEach` intentionally excludes `kUsed` rigor, so code needing usage must use different iteration logic.

## Test Signals

Unit tests for enum-index mapping, set/update/removeEmpty behavior, checksum stability, and all owner/resource combinations are the main confidence signals.
