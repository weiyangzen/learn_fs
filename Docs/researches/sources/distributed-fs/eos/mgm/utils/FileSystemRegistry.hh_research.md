# sources/distributed-fs/eos/mgm/utils/FileSystemRegistry.hh

## Purpose
Declares `FileSystemRegistry`, a compatibility map-like registry for currently registered MGM filesystems with multiple lookup indexes.

## Important APIs, types, and functions
Defines `const_iterator` over the fsid map and exposes `begin()/end()` compatibility methods. Lookup APIs return by id, pointer, queue path, or space. Mutation APIs register, erase, and clear entries. Private `IdAndQueuePath` stores reverse-index metadata.

## Control flow
The public contract requires unique fsid, unique `FileSystem*`, and unique queue path for registration. All indexes are kept in lockstep by the implementation.

## State and persistence behavior
The registry stores raw `mgm::FileSystem*` values but does not own their lifetime. It is in-memory only and protected by `mMutex` for normal methods.

## Dependencies and integration points
Depends on `common/FileSystem.hh`, `mgm/filesystem/FileSystem.hh`, `RWMutex`, and MGM namespace macros. It is a central lookup utility for global filesystem views.

## Risks and test signals
Iterator methods do not acquire locks and should be treated as legacy compatibility hazards. Tests should verify no stale reverse mappings remain after erase and that object lifetime is controlled elsewhere.
