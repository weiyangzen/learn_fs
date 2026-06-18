# sources/distributed-fs/beegfs/common/source/common/storage/EntryInfo.h

## Purpose
Defines the metadata needed to locate or operate on an inode or chunk files: owner metadata node, parent ID, entry ID, file name, type, and feature flags.

## Important APIs, Types, And Functions
Defines `ENTRYINFO_FEATURE_INLINED`, `ENTRYINFO_FEATURE_BUDDYMIRRORED`, `EntryInfo_PARENT_ID_UNKNOWN`, list typedefs, constructors, `set()` overloads, feature-flag setters/getters, field getters, equality, and serialization.

## Control Flow
Serialization writes entry type as `uint32_t`, feature flags, three 4-byte-aligned strings, owner node ID, and padding. Feature setters set or clear individual bits.

## State, Persistence, And Dependencies
This is a serialized value object and must remain synchronized with client-side `EntryInfo.h`. Depends on `NumNodeID` and `StorageDefinitions`.

## Integration Points
Used in metadata messages, inode lookup, path traversal, and client/server protocol contracts.

## Risks
Wire layout changes require client-module updates. `ENTRYINFO_FEATURE_INLINED` may be outdated by design, so callers should not assume it is authoritative without validation.

## Test Signals
Serialization compatibility, flag toggling, owner/parent/entry identity, aligned string handling, and client-module golden vectors are important.
