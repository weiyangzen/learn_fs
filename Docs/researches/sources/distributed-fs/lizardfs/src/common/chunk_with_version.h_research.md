<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_with_version.h -->
# sources/distributed-fs/lizardfs/src/common/chunk_with_version.h

## Purpose

This header defines a minimal serializable pair of chunk id and version.

## Important APIs, Types, and Functions

`LIZARDFS_DEFINE_SERIALIZABLE_CLASS(ChunkWithVersion, uint64_t id, uint32_t version)` generates the value class and serialization methods.

## Control Flow

There is no explicit control flow beyond generated serialization.

## State and Persistence Behavior

Instances carry persistent chunk identity/version data in protocol or metadata messages.

## Dependencies and Integration Points

It depends on serialization macros and fixed-width integer types.

## Risks and Edge Cases

The macro hides generated constructors/operators, so readers must inspect macro definitions for exact behavior. Version flag packing, if needed, is not handled here.

## Test Signals

Serialization round trips and protocol compatibility tests are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_with_version.h -->
