# sources/distributed-fs/eos/mgm/utils/FilesystemUuidMapper.hh

## Purpose
Declares `FilesystemUuidMapper`, a bidirectional uuid-to-fsid utility with allocation support.

## Important APIs, types, and functions
Public methods inject, query, look up, remove, clear, and allocate mappings. The private state is an `RWMutex`, `fs2uuid`, and `uuid2fs`.

## Control flow
The class promises conflict-free injection, sentinel returns (`0` or empty string) for missing lookups, and stable allocation for already-registered UUIDs.

## State and persistence behavior
All state is in-process map state. The class does not store to config or namespace services.

## Dependencies and integration points
Depends on MGM namespace macros, `common/FileSystem.hh`, and `RWMutex`. It is designed for filesystem registration/bootstrap paths that need stable IDs.

## Risks and test signals
The stated 64k capacity affects scalability and failure mode. Tests should verify one-to-one invariants after every public mutation and ensure callers do not treat fsid `0` as allocatable.
