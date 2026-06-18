# sources/distributed-fs/beegfs/common/source/common/storage/EntryInfoWithDepth.h

## Purpose
Extends `EntryInfo` with a 0-based path depth value.

## Important APIs, Types, And Functions
Constructors, `set()`, `getEntryDepth()`, `setEntryDepth()`, and serialization via `serdes::base<EntryInfo>` plus `entryDepth`.

## Control Flow
No complex control flow; it delegates base-field handling to `EntryInfo`.

## State, Persistence, And Dependencies
Adds `uint32_t entryDepth` to the base serialized entry information.

## Integration Points
Used when callers need both entry identity and its depth in a path traversal or listing workflow.

## Risks
Base equality does not include depth unless callers explicitly compare the derived field.

## Test Signals
Serialize/deserialize base plus depth, constructor from base defaults depth to zero, and depth mutation.
