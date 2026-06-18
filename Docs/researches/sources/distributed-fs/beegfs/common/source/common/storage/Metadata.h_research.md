# sources/distributed-fs/beegfs/common/source/common/storage/Metadata.h

## Purpose
Defines metadata directory names, root/disposal IDs, hash fanout constants, and special subdirectory names for BeeGFS metadata storage.

## Important APIs, Types, And Functions
Exports constants for root/disposal IDs, inode and dentry fanout/subdir names, ID-based access subdir marker, lost+found, and buddy mirror subdir.

## Control Flow
No runtime logic.

## State, Persistence, And Dependencies
No state. These constants shape on-disk metadata layout.

## Integration Points
Used by metadata server path construction, recovery, disposal handling, and buddy-mirror metadata storage.

## Risks
Changing constants breaks existing on-disk layouts. The ID-based access subdir marker is noted as potentially conflicting with user names.

## Test Signals
Layout tests should verify generated inode/dentry paths and migration/backward compatibility.
