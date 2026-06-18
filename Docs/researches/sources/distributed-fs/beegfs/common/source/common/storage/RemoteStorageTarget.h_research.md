# sources/distributed-fs/beegfs/common/source/common/storage/RemoteStorageTarget.h

## Purpose
Represents remote storage target policy metadata: version, cooldown period, file policies, and a vector of remote target IDs.

## Important APIs, Types, And Functions
Constructors, `set()`, `reset()`, `hasInvalidIds()`, `hasDuplicateIds()`, `hasInvalidVersion()`, `validateWithDetails()`, serialization, getters, `setRstIds()`, and `toStr()` are provided.

## Control Flow
Default constructor leaves version zero/invalid. Constructors with IDs set default version 1.0, cooldown 120, and default file policy. Validation accumulates human-readable reasons.

## State, Persistence, And Dependencies
State is version bytes, cooldown, reserved field, policy bits, and `rstIdVec`. It serializes all fields. Depends on storage definitions, vectors/sets, and string streams.

## Integration Points
Used by metadata/policy code for files that can refer to remote storage targets.

## Risks
A default-constructed object is invalid until initialized. Validation checks duplicate/zero IDs but not policy semantics or cooldown ranges.

## Test Signals
Validate default invalid object, constructor defaults, reset, duplicate IDs, ID zero, serialization, and `toStr()` formatting.
