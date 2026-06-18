# sources/distributed-fs/beegfs/common/source/common/nodes/OpCounterTypes.h

## Purpose
Defines metadata and storage operation counter enums plus short string mappings for display/export tools.

## Important APIs, Types, And Functions
`MetaOpCounterTypes`, `StorageOpCounterTypes`, and `OpToStringMapping::mapMetaOpNum()`/`mapStorageOpNum()` are the key exports. Sentinel values determine counter vector lengths.

## Control Flow
Mapping functions switch over known enum values and return the numeric value as a string for unknown inputs.

## State, Persistence, And Dependencies
No mutable state. It depends on `StringTk`.

## Integration Points
Used by `OpCounter`, `NodeOpStats`, server operation accounting, and `fhgfs-ctl` presentation.

## Risks
New enum values must be inserted immediately before the sentinel and added to the mapping to preserve compatibility and usability. Byte counters are not intended as independent operation counters.

## Test Signals
Tests should verify every enum except sentinel has a stable nonnumeric mapping and that counter array sizes match sentinel values.
