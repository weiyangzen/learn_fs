# sources/distributed-fs/beegfs/common/source/common/storage/EntryInfo.cpp

## Purpose
Implements equality for `EntryInfo`.

## Important APIs, Types, And Functions
`EntryInfo::operator==()` compares owner node, parent entry ID, entry ID, file name, entry type, and feature flags.

## Control Flow
No branching beyond chained equality.

## State, Persistence, And Dependencies
No extra state. Includes serialization/logging headers through the implementation unit.

## Integration Points
Equality is used by metadata operations, tests, and message handlers that compare file-entry identity.

## Risks
Equality includes `fileName`, so renamed entries with the same entry ID compare different. It ignores any subclass fields such as `EntryInfoWithDepth::entryDepth`.

## Test Signals
Verify equality changes on each field and that base comparisons do not accidentally include derived state.
