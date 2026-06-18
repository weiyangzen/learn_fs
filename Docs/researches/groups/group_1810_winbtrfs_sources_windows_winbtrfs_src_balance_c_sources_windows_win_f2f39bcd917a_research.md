# Group Research: group_1810_winbtrfs_sources_windows_winbtrfs_src_balance_c_sources_windows_win_f2f39bcd917a

Scope confirmed against `Docs/research_subset_a.md`. All four listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/balance.c -->
# File Research: sources/windows/winbtrfs/src/balance.c

## Purpose

`balance.c` implements WinBtrfs balance, chunk relocation, profile conversion, balance resume/pause/stop/query IOCTL support, and device removal/shrink workflows. It moves data and metadata extents out of selected chunks, rewrites extent/backreference metadata, commits the transaction, and coordinates long-running balance state through a kernel thread.

## Core Data Structures

- `metadata_reloc`
  - Tracks a relocated metadata tree block: old address, new address, loaded `tree_header`, original `EXTENT_ITEM`, whether it belongs to system space, associated in-memory `tree`, and metadata refs.
- `metadata_reloc_ref`
  - Represents `TREE_BLOCK_REF` or `SHARED_BLOCK_REF` references for a metadata block.
  - Stores parent relocation state so shared refs can be rewritten from old parent addresses to new parent addresses.
- `data_reloc`
  - Tracks a relocated data extent: old logical address, size, new address, new chunk, original `EXTENT_ITEM`, and data refs.
- `data_reloc_ref`
  - Represents `EXTENT_DATA_REF` or `SHARED_DATA_REF` references for a data extent, with parent metadata relocation for shared refs.
- `BALANCE_UNIT`
  - Limits data relocation reads/writes to 1 MiB at a time.

## Metadata Relocation

- `add_metadata_reloc()`
  - Removes an existing metadata extent item from the extent tree.
  - Decrements old chunk usage and adds the old tree block range back to free space.
  - Parses inline `TREE_BLOCK_REF` and `SHARED_BLOCK_REF` records.
  - Scans following non-inline ref items if the inline refcount is smaller than the extent item refcount.
  - Adds a `metadata_reloc` object to the pending relocation list.
- `add_metadata_reloc_parent()`
  - Reuses an already queued `metadata_reloc` for a parent address when present.
  - Otherwise finds the parent block’s `METADATA_ITEM` or tree `EXTENT_ITEM` and queues it for relocation too.
- `sort_metadata_reloc_refs()`
  - Sorts refs into on-disk order before rebuilding extent items.
- `add_metadata_reloc_extent_item()`
  - Recreates the relocated metadata extent item at the new address.
  - Uses skinny metadata when enabled; otherwise writes `EXTENT_ITEM2` with first item and level.
  - Splits refs between inline refs and separate ref items when inline data would exceed one quarter of node size.
  - Rewrites shared metadata/data backrefs inside child tree blocks or leaf extent-data items when the parent block address changes.

## Metadata Write Path

`write_metadata_items()` is the central metadata relocation writer:

- Reads each old tree block into memory.
- Detects whether the original block came from system space.
- If data relocation is also in progress, updates leaf `EXTENT_DATA` physical addresses from old data extents to new data extents.
- Finds parent tree blocks or root items that refer to each moved block.
- Allocates new metadata addresses by level, preferring a recently allocated chunk, then compatible existing chunks, then a new chunk.
- Updates parent internal-node pointers, loaded tree-data holders, root treeholder addresses, and superblock root/chunk tree addresses.
- Updates in-memory tree hash lists when a loaded tree’s address changes.
- Recomputes tree checksums and queues physical tree writes.
- Calls `do_tree_writes()` and then recreates relocated metadata extent items.
- Cleans up queued `tree_write` records on exit.

`balance_metadata_chunk()` scans the extent tree for metadata extents in a selected chunk, queues up to 64 metadata blocks per pass, calls `write_metadata_items()`, commits via `do_write()`, applies rollback on failure, frees cached trees, and reports whether anything changed.

## Data Relocation

- `data_reloc_add_tree_edr()`
  - Resolves an `EXTENT_DATA_REF` to the owning root/inode.
  - Scans the file’s `EXTENT_DATA` items to find references to the relocating extent.
  - Groups adjacent references from the same leaf tree.
  - Adds the containing leaf tree to metadata relocation so the file extent item can be rewritten.
- `add_data_reloc()`
  - Deletes the old data extent item.
  - Decrements old chunk usage and frees the old logical range.
  - Parses inline and non-inline `EXTENT_DATA_REF` / `SHARED_DATA_REF` records.
  - For shared data refs, queues the parent metadata block for relocation.
- `sort_data_reloc_refs()`
  - Sorts refs by type/hash and coalesces duplicate `EXTENT_DATA_REF` records by summing counts.
- `add_data_reloc_extent_item()`
  - Recreates the relocated data extent item at the new address.
  - Emits inline refs up to the node-size limit and separate ref items beyond that.

`balance_data_chunk()` relocates actual file data:

- Scans data `EXTENT_ITEM`s in a selected chunk, excluding tree-block extents.
- Processes at most 16 MiB or 100 extents per pass.
- Allocates destination data ranges from compatible non-reloc chunks or a newly allocated data chunk.
- Builds a bitmap of sectors with checksums by reading checksum-tree items.
- Copies no-checksum and checksum-covered runs in `BALANCE_UNIT` chunks.
- For checksum-covered runs, verifies reads using old checksums, writes data to the new extent, inserts new checksum items, and removes old checksum items.
- Calls `write_metadata_items()` for the metadata leaves that point at moved extents.
- Recreates data extent items at the new logical addresses.
- Moves matching `changed_extent` records to the destination chunk.
- Updates free-space-cache inode extents before commit and open FCB extent mappings after successful commit.
- Commits through `do_write()`, clears or rolls back relocation state, frees cached trees, and releases relocation objects.

## Balance Filters And Persistent State

- `get_chunk_dup_type()` extracts the chunk’s profile: single, dup, RAID0/1/10/5/6/1C3/1C4.
- `should_balance_chunk()` applies per-class balance filters:
  - enabled flag
  - profiles
  - device id
  - device range
  - virtual range
  - stripe count
  - usage percentage
  - soft convert skip when already in target profile
- `copy_balance_args()` converts in-memory `btrfs_balance_opts` to on-disk `BALANCE_ARGS`.
- `add_balance_item()` writes a root-tree `BALANCE_ITEM` so an interrupted balance can be resumed.
- `remove_balance_item()` deletes the persistent balance item after a normal balance completes.
- `load_balance_args()` reconstructs in-memory balance options from a persisted `BALANCE_ITEM`.
- `look_for_balance_item()` is the mount-time/resume path:
  - finds `BALANCE_ITEM`;
  - loads data/metadata/system options;
  - applies Linux-like heuristics: convert balances become soft, and non-convert balances without usage filters get a 0-90% usage filter;
  - pauses if readonly or `skip_balance` is set;
  - starts `balance_thread()`.

## Device Removal And Shrink

- `remove_device()` validates privilege, target device existence, readonly state, active balance state, and RAID minimum-device constraints.
  - It refuses to remove the last writable device.
  - It rejects removals that would violate RAID0/1/5/6/10/1C3/1C4 requirements.
  - It starts a balance in removal mode with all chunk classes filtered by `devid`.
- `finish_removing_device()`
  - Flushes outstanding writes.
  - Removes the device’s `DEV_ITEM` and `DEV_STATS`.
  - Decrements superblock device counters and total size.
  - Commits the removal.
  - Zeroes superblocks on the removed device when writable.
  - Updates the volume child list and mount manager state.
  - Re-adds drive letters for a removed child that previously had one.
  - Updates removable-media characteristics, trim state, and notifies volume-size change.
- `trim_unalloc_space()`
  - Builds TRIM ranges for all unallocated device regions, avoiding superblock locations and the first MiB.
  - Issues `IOCTL_STORAGE_MANAGE_DATA_SET_ATTRIBUTES` with `DeviceDsmAction_Trim`.
- `regenerate_space_list()`
  - Rebuilds a device’s free-space list after shrink failure/cancel by starting with all space after the first MiB and subtracting every stripe allocation.
- Shrink completion in `balance_thread()` updates `devitem.num_bytes`, rewrites the device item, adjusts `superblock.total_bytes`, commits, or regenerates the space list on failure.

## Balance Thread Control Flow

`balance_thread()` is the long-running kernel worker:

1. Increments `balance_num` and initializes thread state.
2. Applies requested profile conversions by changing `Vcb->data_flags`, `metadata_flags`, and `system_flags`.
3. Mirrors data/metadata options for mixed block groups.
4. Writes `BALANCE_ITEM` for normal balances, or flushes pending writes for removal/shrink.
5. Waits on `Vcb->balance.event`, supporting pause/resume.
6. Scans chunks and builds a selected chunk list using `should_balance_chunk()`.
7. Loads chunk free-space caches before relocation.
8. For full balances with no already-acceptable chunks, preallocates a destination chunk or calls `try_consolidation()`.
9. Marks selected chunks as `reloc`.
10. Relocates data chunks first, then metadata/system chunks.
11. On stop/error, clears relocation flags and restores old profile flags.
12. Finishes device removal or shrink when requested.
13. Removes the persistent balance item for normal balances.
14. Trims unallocated space after successful operations when enabled.
15. Closes the thread handle, clears `Vcb->balance.thread`, and signals `balance.finished`.

`try_consolidation()` supports out-of-space full balances by relocating least-used data chunks not yet handled in the current balance, then allocating a destination chunk.

## Public Entry Points

- `start_balance()`
  - IOCTL entry point for starting a balance.
  - Requires `SE_MANAGE_VOLUME_PRIVILEGE`.
  - Rejects locked volumes, active scrub, active balance, readonly volumes, and empty option sets.
  - Validates profile, devid, range, limit, stripe, usage, and convert options.
  - Copies options into `Vcb->balance`, initializes events/status, and starts `balance_thread()`.
- `query_balance()`
  - Reports stopped/running/paused status, removal/shrink flags, error status, chunks left/total, and active options.
- `pause_balance()`
  - Requires privilege, active running balance, and clears the balance event.
- `resume_balance()`
  - Requires privilege, active paused balance, writable volume, and sets the balance event.
- `stop_balance()`
  - Requires privilege, marks the balance as stopping, clears paused state, sets success status, and wakes the thread.

## Important Dependencies

This file depends heavily on WinBtrfs transaction and tree helpers:

- tree search/mutation: `find_item`, `find_next_item`, `find_item_to_level`, `insert_tree_item`, `delete_tree_item`
- extent accounting: `increase_extent_refcount`, `decrease_extent_refcount`, `find_extent_shared_tree_refcount`, `find_extent_shared_data_refcount`
- allocation/free space: `alloc_chunk`, `find_metadata_address_in_chunk`, `find_data_address_in_chunk`, `space_list_add`, `space_list_subtract`, `load_cache_chunk`
- I/O: `read_data`, `write_data_complete`, `write_data_phys`, `do_tree_writes`
- transaction control: `do_write`, `clear_rollback`, `do_rollback`, `free_trees`
- checksum tree updates: `add_checksum_entry`
- Windows kernel primitives: `ERESOURCE`, `KEVENT`, `PsCreateSystemThread`, `ZwClose`, `FsRtlNotifyVolumeEvent`, storage TRIM IOCTLs, mount manager IOCTLs

## Notable Edge Cases

- `start_balance()` appears to normalize `USAGE` using `stripes_start` / `stripes_end` instead of `usage_start` / `usage_end`, and checks the stripe fields for the usage range. That looks like a validation bug.
- `should_balance_chunk()` checks `num_stripes < stripes_start || num_stripes < stripes_end`; the second comparison likely should reject values above `stripes_end`.
- Several relocation helpers mutate extent-tree and chunk free-space state before later allocations or tree rewrites can fail. Rollback lists are used, but correctness depends on every changed path being represented in rollback state.
- Some allocation-failure paths after deleting tree items or extent refs return directly and rely on the outer rollback/commit structure; leaks of partially allocated relocation refs are possible until the end cleanup walks the lists.
- `balance_thread()` owns long-running state through shared `Vcb->balance` fields without a single dedicated balance lock; correctness depends on event/state discipline and existing tree/chunk locks.
- Device removal updates mount-manager and child-device structures after on-disk commit, so failures in those later notification paths are logged but do not roll back the filesystem removal.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/balance.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/blake2-impl.h -->
# File Research: sources/windows/winbtrfs/src/blake2-impl.h

## Purpose

`blake2-impl.h` is the local BLAKE2 support header used by WinBtrfs’s reference BLAKE2b implementation. It provides endian-safe load/store helpers, rotate helpers, packing macros, constants, and the `blake2b_state` / `blake2b_param` structures.

## Main Contents

- Defines `BLAKE2_INLINE` depending on C/C++ mode and compiler.
- Forces `NATIVE_LITTLE_ENDIAN`, which matches supported Windows targets.
- Provides inline little-endian helpers:
  - `load16`, `load32`, `load48`, `load64`
  - `store16`, `store32`, `store48`, `store64`
- Provides rotate helpers:
  - `rotr32`
  - `rotr64`
- Defines `BLAKE2_PACKED` for MSVC and GCC-style compilers.
- Defines BLAKE2b constants:
  - block size: 128 bytes
  - output size: 64 bytes
  - key size: 64 bytes
  - salt/personalization size: 16 bytes each
- Defines `blake2b_state`:
  - chaining words `h[8]`
  - byte counter `t[2]`
  - finalization flags `f[2]`
  - 128-byte buffer
  - buffer length, output length, last-node flag
- Defines packed `blake2b_param`:
  - digest/key/fanout/depth fields
  - leaf/node/xof fields
  - reserved area
  - salt and personalization arrays

## Implementation Notes

- On native little-endian builds, load/store uses `memcpy`, avoiding unaligned access and strict-aliasing problems.
- Non-little-endian fallback code exists for 16/32/64-bit helpers, but the header unconditionally defines `NATIVE_LITTLE_ENDIAN`.
- `load48` and `store48` are byte-wise helpers independent of native-endian mode.
- The file contains only static inline helpers and type definitions; it exports no standalone function.

## Integration

`blake2b-ref.c` includes this header for BLAKE2b compression, initialization, update, and finalization. WinBtrfs uses BLAKE2b as one of the supported Btrfs checksum algorithms elsewhere in the driver.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/blake2-impl.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/blake2b-ref.c -->
# File Research: sources/windows/winbtrfs/src/blake2b-ref.c

## Purpose

`blake2b-ref.c` is a compact reference implementation of unkeyed BLAKE2b hashing. In WinBtrfs it supplies the hash primitive used when the filesystem checksum type is BLAKE2.

## Main Constants

- `blake2b_IV[8]`
  - Standard BLAKE2b initialization vector.
- `blake2b_sigma[12][16]`
  - Standard message word permutation schedule for 12 compression rounds.

## Main Routines

- `blake2b_init0()`
  - Clears the state and initializes `h[]` from the IV.
- `blake2b_init_param()`
  - XORs the BLAKE2b parameter block into the IV-derived state.
  - Stores the requested digest length.
- `blake2b_init()`
  - Builds a default unkeyed parameter block:
    - digest length from caller
    - fanout 1
    - depth 1
    - zero salt/personalization/reserved fields
- `blake2b_increment_counter()`
  - Adds processed bytes to the 128-bit byte counter.
- `blake2b_set_lastnode()`, `blake2b_is_lastblock()`, `blake2b_set_lastblock()`
  - Manage final-block flags.
- `blake2b_compress()`
  - Loads 16 little-endian message words.
  - Initializes the 16-word working vector from state, IV, counters, and finalization flags.
  - Runs 12 `ROUND()` invocations using the BLAKE2b `G()` mixing function.
  - Folds the working vector back into `S->h`.
- `blake2b_update()`
  - Buffers partial input.
  - Compresses full 128-byte blocks.
  - Leaves the last block uncompressed until finalization.
- `blake2b_final()`
  - Validates output buffer and state.
  - Increments counter by remaining buffered bytes.
  - Marks the final block.
  - Pads the buffer with zeros, compresses, stores the 64-byte digest to a temporary buffer, and copies the requested digest length.
- `blake2b()`
  - Public wrapper: initialize, update once, finalize.

## Behavior

The exposed `blake2b()` interface supports one-shot unkeyed hashing with caller-selected output length. It does not expose keyed hashing, streaming state, salt, personalization, tree hashing, or XOF behavior to callers.

## Notable Details

- `blake2b_final()` returns an error for null output or too-small output, but `blake2b()` ignores return values from `update()` and `final()`.
- `blake2b_init()` casts `outlen` to `uint8_t` without explicit range validation. Normal Btrfs use should request a valid digest length.
- The implementation includes `<stdio.h>` but does not use it.
- Input length is `size_t`; a comment notes that `inlen` ideally should be `uint64_t`.
- The code is reference-oriented rather than platform-optimized.

## Integration

The implementation depends on `blake2-impl.h` for endian helpers, state/parameter definitions, constants, and rotate operations. Driver checksum code can call `blake2b(out, outlen, in, inlen)` as a simple one-shot digest primitive.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/blake2b-ref.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/boot.c -->
# File Research: sources/windows/winbtrfs/src/boot.c

## Purpose

`boot.c` contains WinBtrfs boot-volume discovery and early boot-device registration support. It identifies whether `\SystemRoot` points to a Btrfs ARC path, extracts the boot filesystem UUID, parses a boot subvolume option, and forces device registration/notifications so the Windows boot volume is available early enough.

## Global State

- `BTRFS_UUID boot_uuid`
  - Boot filesystem UUID parsed from `\SystemRoot` / `\Device\BootDevice` symbolic link targets.
- `uint64_t boot_subvol`
  - Optional boot subvolume ID parsed from `SystemStartOptions`.

## Boot Root Discovery

`get_system_root()`:

- Opens the `\SystemRoot` symbolic link.
- Queries the link target length, allocates a buffer, and reads the target.
- If `\SystemRoot` points at `\Device\BootDevice`, follows that symbolic link too.
- Logs the discovered target.
- Checks for an ARC path prefix `\ArcName\btrfs(`.
- Parses a UUID in text form from the path:
  - two hex digits per byte
  - hyphens after UUID byte indexes 3, 5, 7, and 9
  - closing `)` after the UUID
- Stores the result in `boot_uuid`.
- Returns `true` only for a valid Btrfs ARC boot path.

## Mount Manager Notification

`mountmgr_notification(BTRFS_UUID* uuid)`:

- Opens the mount manager device.
- Builds a `MOUNTMGR_TARGET_NAME` using `BTRFS_VOLUME_PREFIX` plus the UUID text form.
- Sends `IOCTL_MOUNTMGR_VOLUME_ARRIVAL_NOTIFICATION`.
- Frees the allocated target-name buffer.

This is used after forcibly adding a boot device so mount manager sees the Btrfs volume arrival.

## Boot Options

`check_boot_options()`:

- Opens `\Registry\Machine\SYSTEM\CurrentControlSet\Control`.
- Queries `SystemStartOptions`.
- Searches for `SUBVOL=`.
- Parses following hex digits into `boot_subvol`.
- Logs the parsed subvolume when nonzero.
- Uses structured exception handling around registry/string access.

## Device Addition

`boot_add_device(DEVICE_OBJECT* pdo)`:

- Calls `AddDevice(drvobj, pdo)` manually for the target PDO.
- Sets `pdode->dont_report = true`.
- Clears `DOE_START_PENDING` on the PDO’s `DeviceObjectExtension`.
- If the volume child device exists, clears `DOE_START_PENDING` on it too.
- Calls `mountmgr_notification()` for the volume UUID.

The explicit `DOE_START_PENDING` clearing is there because early boot code may need `NtOpenFile` to succeed before normal PnP relation reporting finishes.

## Public Boot Check

`check_system_root()`:

- Waits for any in-progress boot PnP notification by acquiring and releasing `boot_lock`.
- Calls `get_system_root()`.
- Scans global `pdo_list` under `pdo_list_lock` for a PDO whose UUID matches `boot_uuid`.
- If the PDO has no volume device extension yet, saves it for manual `boot_add_device()`.
- If `AddDevice` already ran, marks both the child device and PDO with `DO_SYSTEM_BOOT_PARTITION`.
- Toggles the bus device interface off and on so Windows reobserves the boot partition state.
- Releases `pdo_list_lock`.
- Parses boot options.
- Calls `boot_add_device()` when a matching PDO must be added manually.

## Important Dependencies

- External globals:
  - `pdo_list_lock`
  - `pdo_list`
  - `boot_lock`
  - `drvobj`
- Driver helpers/macros:
  - `AddDevice`
  - `dev_ioctl`
  - `hex_digit`
  - `mountmgr_add_drive_letter` indirectly through nearby device flows
  - `BTRFS_VOLUME_PREFIX`
- Windows kernel APIs:
  - `ZwOpenSymbolicLinkObject`
  - `ZwQuerySymbolicLinkObject`
  - `ZwOpenKey`
  - `ZwQueryValueKey`
  - `IoGetDeviceObjectPointer`
  - `IoSetDeviceInterfaceState`
  - `ExAcquireResource*`
  - `ExAllocatePoolWithTag`
  - `ExFreePool`

## Notable Details

- `DEVOBJ_EXTENSION2` is a local partial definition used only to reach `ExtensionFlags` and clear `DOE_START_PENDING`.
- `check_boot_options()` has FIXME comments:
  - it uses a fixed 255-WCHAR buffer and should not fail for longer values;
  - it writes a terminator at `options[DataLength / sizeof(WCHAR)]` and notes the buffer-size assumption.
- `mountmgr_notification()` returns without dereferencing `FileObject` if allocation of `mmtn` fails, which appears to leak the mount manager file object on that path.
- `boot_add_device()` dereferences `pdode` before verifying it is non-null; expected callers pass WinBtrfs PDOs.
- The UUID parser is strict about hex digits, hyphen positions, and closing parenthesis, and returns false on malformed paths.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/boot.c -->