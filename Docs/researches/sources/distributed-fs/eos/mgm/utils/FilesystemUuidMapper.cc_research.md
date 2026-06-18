# sources/distributed-fs/eos/mgm/utils/FilesystemUuidMapper.cc

## Purpose
Implements a thread-safe bidirectional map between filesystem IDs and UUID strings.

## Important APIs, types, and functions
`injectMapping()` validates positive id/non-empty UUID and rejects conflicting existing mappings. `hasFsid()`, `hasUuid()`, `size()`, and both `lookup()` overloads are read operations. `remove()` by id or UUID deletes both directions. `clear()` drops all mappings. `allocate()` returns an existing id for a known UUID or assigns a free id, preferring max+1 below 64000 and then scanning for holes.

## Control flow
All methods take read or write locks. Mutations maintain `uuid2fs` and `fs2uuid` together. Allocation starts at 1 for an empty map, uses increasing ids when possible, falls back to linear search, and aborts the process if all ids are exhausted.

## State and persistence behavior
State is in-memory only: `fs2uuid` and `uuid2fs`. Persistence of mappings, if any, is external to this class.

## Dependencies and integration points
Uses `RWMutex`, EOS assertions/logging, and `common::FileSystem::fsid_t`. It replaces/encapsulates legacy FsView uuid-fsid mapping behavior.

## Risks and test signals
`allocate()` does not reject an empty UUID, unlike `injectMapping()`. Exhaustion calls `exit(-1)`, which is severe for a library-like utility. The 64000 cap is a legacy limit. Tests should cover id/UUID conflicts, id 0 rejection, empty UUID injection rejection, empty UUID allocation behavior, hole reuse above max threshold, remove consistency, and concurrent allocation.
