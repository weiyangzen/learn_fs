# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/constants.h

## Purpose

`constants.h` centralizes VDO-wide fixed limits and defaults used by the data path, block map, journals, slabs, thread configuration, and block sizing. These constants define major layout and scalability assumptions for the VDO target.

## Important APIs, Types, And Functions

- Block-map geometry: `VDO_BLOCK_MAP_ENTRIES_PER_PAGE`, `VDO_BLOCK_MAP_FLAT_PAGE_ORIGIN`, `VDO_BLOCK_MAP_TREE_HEIGHT`, and `DEFAULT_VDO_BLOCK_MAP_TREE_ROOT_COUNT`.
- I/O submission defaults: `VDO_BIO_ROTATION_INTERVAL_LIMIT`, `DEFAULT_VDO_BIO_SUBMIT_QUEUE_COUNT`, and `DEFAULT_VDO_BIO_SUBMIT_QUEUE_ROTATE_INTERVAL`.
- Journal and slab defaults: `DEFAULT_VDO_RECOVERY_JOURNAL_SIZE`, `DEFAULT_VDO_SLAB_JOURNAL_SIZE`, and `RECOVERY_JOURNAL_STARTING_SEQUENCE_NUMBER`.
- Lock and restoration limits: `VDO_LOCK_MAP_CAPACITY` and `MAXIMUM_SIMULTANEOUS_VDO_BLOCK_MAP_RESTORATION_READS`.
- Zone and thread limits: `MAX_VDO_LOGICAL_ZONES`, `MAX_VDO_PHYSICAL_ZONES`, and `MAXIMUM_VDO_THREADS`.
- Slab sizing: `DEFAULT_VDO_SLAB_BLOCKS`, `MIN_VDO_SLAB_BLOCKS`, `MAX_VDO_SLAB_BLOCKS`, and `MAX_VDO_SLABS`.
- Request/block sizing: `MAXIMUM_VDO_USER_VIOS`, `VDO_BLOCK_SIZE`, `VDO_SECTORS_PER_BLOCK`, `VDO_SECTOR_SIZE`, and `VDO_ZERO_BLOCK`.

## Control Flow

This header contains no runtime control flow. Its enum constants are compiled into allocation sizing, validation, tree traversal, bio splitting/submission, and on-disk layout calculations throughout VDO.

## State And Persistence Behavior

Several constants affect persistent format interpretation. `VDO_BLOCK_SIZE`, block-map geometry, journal sizes, root count defaults, slab limits, and `VDO_ZERO_BLOCK` are baked into block-map pages, journal behavior, and physical-space layout. Changing them would require coordinated format migration.

## Dependencies And Integration Points

The file includes Linux block-device definitions for `SECTOR_SHIFT` and VDO `types.h`. It is used by block-map code, data VIOs, slab depot, journals, thread configuration, I/O submitters, and format/configuration code.

## Risks And Edge Cases

- `VDO_BLOCK_MAP_ENTRIES_PER_PAGE` must match the packed on-disk `struct block_map_page` size; `block-map.c` has a `BUILD_BUG_ON` for this.
- `VDO_BLOCK_SIZE` is assumed to be 4096 and not larger than `PAGE_SIZE` in `data-vio.c`.
- Zone/thread maxima constrain configuration validation and array sizing.
- `VDO_ZERO_BLOCK` is a reserved physical block for zero mappings; treating it as an allocatable data block would corrupt zero/discard semantics.

## Test Signals

Build-time checks should catch block-map entry count and block size assumptions. Configuration tests should cover min/default/max slab blocks, maximum zones/threads, journal defaults, and correct sector/block conversions for partial bios and discards.
