# sources/distributed-fs/beegfs/common/source/common/storage/StorageDefinitions.h

## Purpose
Defines shared storage flags, file entry types, file inode modes, settable attributes, lock request types, and target path/fd maps.

## Important APIs, Types, And Functions
Exports open flags/masks, setattr flags, entry lock flags/masks, `DirEntryType`, `FileInodeMode`, `EntryLockRequestType`, `SettableFileAttribs`, `TargetPathMap`, and `TargetFDMap`. `DirEntryType` serializes as `uint8_t` and has stream/macro helpers.

## Control Flow
No complex logic; macros classify entry types and stream output maps enum values to readable names.

## State, Persistence, And Dependencies
No global state. The header must stay in sync with the client module because flags and enum values cross user/kernel/server boundaries.

## Integration Points
Used by `EntryInfo`, `StatData`, open/setattr/locking messages, and storage target path management.

## Risks
Changing numeric flag/enum values breaks protocol and on-disk expectations. Macros do not provide type safety.

## Test Signals
Client/server header compatibility, stream output, macro classification, and serialization width should be checked.
