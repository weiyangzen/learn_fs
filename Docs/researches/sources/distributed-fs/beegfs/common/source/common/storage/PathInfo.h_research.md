# sources/distributed-fs/beegfs/common/source/common/storage/PathInfo.h

## Purpose
Represents chunk-location metadata for a file, including original parent UID/entry ID and flags for layout generation and stub files.

## Important APIs, Types, And Functions
Defines `PATHINFO_FEATURE_ORIG`, `PATHINFO_FEATURE_ORIG_UNKNOWN`, `PATHINFO_FEATURE_IS_STUB`, list typedefs, constructors, setters/getters, `hasOrigFeature()`, `isStub()`, equality, and serialization.

## Control Flow
Serialization always writes flags and conditionally writes `origParentUID` and aligned `origParentEntryID` only if `PATHINFO_FEATURE_ORIG` is set.

## State, Persistence, And Dependencies
State is `flags`, `origParentUID`, and `origParentEntryID`. It is a protocol/disk value object.

## Integration Points
Used by metadata and storage code to locate chunk files across old/new layout schemes and to mark stub files.

## Risks
If the ORIG flag is absent, original parent fields are not serialized, so consumers must respect the flag. `PATHINFO_FEATURE_ORIG_UNKNOWN` requires later resolution.

## Test Signals
Round-trip with and without ORIG, stub flag detection, equality on static fields, and migration from old 2012.10 to 2014.01-style layout.
