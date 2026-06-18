<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map-metadata.h -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map-metadata.h

## Purpose
Declares the metadata-space-map API and constants for the self-hosting metadata allocator used by the persistent-data transaction manager.

## Important APIs, Types, And Functions
`DM_SM_METADATA_BLOCK_SIZE` fixes the metadata block size in sectors for this implementation. `DM_SM_METADATA_MAX_BLOCKS` and `DM_SM_METADATA_MAX_SECTORS` describe the current limit imposed by one metadata index block with 255 entries, each covering roughly 16k metadata blocks.

`dm_sm_metadata_init()` allocates an uninitialized space-map object. `dm_sm_metadata_create()` initializes it for a fresh metadata device, given a transaction manager, block count, and superblock location. `dm_sm_metadata_open()` loads an existing root.

## Control Flow
The header documents the two-phase construction caused by the transaction-manager/space-map cycle: callers first allocate/init the space-map object, then create/open it once the transaction manager can refer back to it.

## State And Persistence
The metadata map persists the same root shape as common space maps but has stricter size limits and self-allocation semantics. The superblock location is excluded/reserved during create so metadata allocation does not overwrite it.

## Dependencies And Integration Points
The header depends on `dm-transaction-manager.h` and is used by the transaction-manager constructors that create/open a transaction manager with its metadata space map.

## Risks
The hard maximum metadata size is part of the API. Callers that expose larger metadata devices must clamp or reject sizes consistently. Incorrect superblock location handling can mark the superblock as free. Two-phase construction requires correct cleanup on errors.

## Test Signals
Signals include create/open root round trips, size clamping at `DM_SM_METADATA_MAX_BLOCKS`, superblock reservation, and transaction-manager create/open integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map-metadata.h -->
