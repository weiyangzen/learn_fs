<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map-metadata.c -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map-metadata.c

## Purpose
Implements the self-hosting metadata `dm_space_map`. This map manages the metadata blocks used by the transaction manager and low-level space-map structures themselves, so it must handle recursive allocation safely while preserving copy-on-write transaction semantics.

## Important APIs, Types, And Functions
`struct sm_metadata` embeds `struct dm_space_map`, current and committed low-level maps, allocation cursor `begin`, recursion depth, per-transaction allocation count, a ring buffer of deferred block operations, and an edge-triggered free-space threshold callback.

Recursive operation support is built from `struct bop_ring_buffer`, `add_bop()`, `apply_bops()`, `in()`, `out()`, `recursing()`, and `combine_errors()`. Normal operations implement count lookup, `count_is_more_than_one`, set/inc/dec, new block, commit, root size/copy, threshold registration, and extend. Bootstrap mode uses `bootstrap_ops` to allocate linearly while creating or extending the self-hosted structures.

Public functions are `dm_sm_metadata_init()`, `dm_sm_metadata_create()`, and `dm_sm_metadata_open()`. The implementation also enforces `DM_SM_METADATA_MAX_BLOCKS` from the header during create.

## Control Flow
Create allocates `sm_metadata`, switches temporarily to bootstrap operations, creates the low-level metadata index and overflow btree, extends the map, then switches to normal ops. It records all blocks consumed by the superblock and initial metadata structures as pending increments, applies those operations, and commits.

Normal inc/dec operations either defer into `uncommitted` when already recursing or enter the recursion guard, perform the low-level update, and on the outermost exit apply deferred operations. `new_block` finds a block free in both old and current maps, advances the cursor, increments it immediately or defers the increment if recursive, tracks `allocated_this_transaction`, and checks the threshold callback after allocation.

Extend switches back to bootstrap mode and starts allocation at the old end. It extends low-level bitmap coverage, then repeatedly records and applies increments for newly consumed metadata blocks and commits until no additional blocks are allocated by the commit itself. Open loads the low-level root, initializes runtime counters and threshold state, and snapshots `old_ll`.

## State And Persistence
Persistent state is the shared `disk_sm_root`, fixed metadata index, bitmap blocks, and overflow refcount btree. Runtime-only state includes recursion depth, deferred operation ring, allocation cursor, per-transaction allocation count, and threshold edge state. Free-space reporting subtracts blocks allocated in the current transaction from the committed free count.

## Dependencies And Integration Points
This file depends on the generic `dm_space_map` API, common low-level space-map code, transaction manager, device-mapper logging, and Linux allocation helpers. It is tied into `dm_tm_create_with_sm()`/`dm_tm_open_with_sm()` to solve the cyclic dependency between transaction manager and metadata allocator.

## Risks
Recursive allocation is the central risk. If the deferred operation ring overflows or operations are applied at the wrong recursion depth, refcounts for metadata blocks can become wrong. `set_count()` is explicitly rejected while recursing because arbitrary overwrite semantics are unsafe there. Threshold callbacks are edge-triggered and must not assume repeated calls while below threshold. Extend must account for metadata allocated by its own commit loop or new metadata blocks could be left marked free.

## Test Signals
Tests should create and open metadata maps, allocate blocks during operations that themselves allocate metadata, force overflow of counts into the refcount btree, extend near and beyond current coverage, verify threshold callback edge behavior, ensure current-transaction freed blocks are not reallocated early, and check root copy/open after commits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map-metadata.c -->
