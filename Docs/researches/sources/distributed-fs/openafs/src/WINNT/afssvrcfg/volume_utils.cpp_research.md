<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/volume_utils.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/volume_utils.cpp

## Purpose
Builds and refreshes a FastList of local drives suitable or unsuitable for AFS partition use.

## Important APIs, Types, And Functions
`SetupDriveList` initializes image lists, columns, and sorting. `UpdateDriveList` clears and repopulates. Internals include `DRIVE_INFO`, `GetDriveInfo`, `FillDriveList`, drive-size/data/recycle-bin/Windows-directory checks, and `DriveListSortFunc`.

## Control Flow
Refresh reads the partition table, iterates logical fixed drives, reads volume info, validates existing AFS, compression, NTFS, and data presence, then inserts rows with normal, warning, disabled, or AFS icons.

## State And Persistence
Module-static `m_hDriveList` stores the target control. The file reads filesystem/partition state and writes only UI rows.

## Dependencies And Integration Points
Depends on Win32 volume APIs, FastList/image lists, resource icons/strings, and partition utilities `ReadPartitionTable`/`IsAnAfsPartition`.

## Risks And Edge Cases
Data-on-drive is warning-like despite error resource naming. `OnlyHasFolder` examines first root entry only. `DoesDriveContainNT` and recycle-bin policy are effectively unused after commented requirements.

## Test Signals
Fixed/removable drives, NTFS/non-NTFS, compressed/existing-AFS/data drives, empty labels, disabled selection, and sort order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/volume_utils.cpp -->
