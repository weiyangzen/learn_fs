<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_with_version_and_type.h -->
# sources/distributed-fs/lizardfs/src/common/chunk_with_version_and_type.h

## Purpose

This header defines serializable chunk id/version/type records with legacy and modern chunk part type encodings.

## Important APIs, Types, and Functions

Both `legacy::ChunkWithVersionAndType` and modern `ChunkWithVersionAndType` store `uint64_t id`, `uint32_t version`, and a chunk part type. They provide constructors, `toString()`, ordering, equality, and serialization. The modern type can construct from the legacy type.

## Control Flow

`toString()` formats hex chunk id and version plus the part type string. Comparisons order by `(id, version, type)`.

## State and Persistence Behavior

Instances are wire/storage value records for chunk metadata. Modern and legacy types preserve compatibility across protocol versions.

## Dependencies and Integration Points

It depends on `ChunkPartType`, `slice_traits`, and serialization macros.

## Risks and Edge Cases

String output is hex and zero-padded, which is useful for diagnostics but should not be parsed unless explicitly documented. Legacy-to-modern conversion is straightforward; modern-to-legacy can lose unsupported type information elsewhere.

## Test Signals

Expected signals are serialization compatibility, ordering behavior, and string output for standard/XOR/EC types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/chunk_with_version_and_type.h -->
