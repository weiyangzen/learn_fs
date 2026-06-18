# sources/distributed-fs/beegfs/common/source/common/storage/Path.h

## Purpose
Implements a small normalized path value type with cached separator offsets, component access, concatenation, comparison, and serialization.

## Important APIs, Types, And Functions
Constructors/assignment, `str()`, `absolute()`, `front()`, `back()`, `empty()`, `dirname()`, `size()`, `operator[]`, `/=` overloads, `/` friends, equality, stream output, and serializer/deserializer functions are provided.

## Control Flow
Construction and deserialization call `updateDirSeparators()`, which compresses consecutive slashes and removes a trailing slash. Component access uses cached separator positions and throws `std::out_of_range` for invalid indexes. Concatenation rejects absolute right-hand paths and updates separator offsets incrementally.

## State, Persistence, And Dependencies
State is `pathStr` plus `dirSeparators`. Serialization stores only the string and rebuilds separators. Depends on serialization, strings, vectors, exceptions, and debug logging.

## Integration Points
Used wherever common code needs normalized path manipulation without repeatedly parsing slashes.

## Risks
`updateDirSeparators()` does not clear `dirSeparators` before repopulating, so assignment/deserialization after prior content can leave stale offsets unless object lifecycle avoids that; this deserves tests. Absolute root path `/` normalizes to an empty string after trailing slash removal, which may be significant. Concatenation throws on absolute RHS.

## Test Signals
Test repeated assignment/deserialization, duplicate slashes, trailing slash, root path, absolute/relative indexing, dirname of single component, concatenation with empty paths, absolute RHS exceptions, and serialization round trips.
