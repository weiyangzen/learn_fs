# File Research: sources/block-storage/mdadm/mapfile.c

## Role

`mapfile.c` maintains mdadm’s runtime map from md kernel device names to metadata type, array UUID, and user-facing device path. It is primarily used by incremental assembly and udev naming so partially assembled arrays can be tracked consistently.

## File Format

The map file is line-oriented and space-separated:

- md device name, such as `md0` or `md_d0`
- metadata string, such as `0.90`, `1.2`, `ddf`, or `imsm`
- UUID as four colon-separated 32-bit hex words
- path, typically under `/dev/md/`

Default paths are derived from `MAP_DIR` and `MAP_FILE`; companion `.new` and `.lock` files provide atomic writes and locking.

## Major Functions

- `open_map()` opens the requested map, new-map, lock, or directory path and creates the map directory when needed.
- `map_write()` writes non-bad entries to the `.new` file, checks stream errors, and atomically renames it over the live map.
- `map_lock()` opens/flocks the lock file, detects stale unlinked lock files, frees any caller-supplied map, and reloads the map.
- `map_unlock()` unlinks and closes the lock and frees the caller’s map.
- `map_fork()` closes inherited lock state around fork without flushing.
- `map_add()`, `map_read()`, `map_free()`, `map_update()`, `map_delete()`, and `map_remove()` implement list and persistence operations.
- `map_by_uuid()`, `map_by_devnm()`, and `map_by_name()` perform lookups and mark entries `bad` when `mddev_busy()` shows the md device is no longer active.
- `RebuildMap()` reconstructs the map by reading mdstat, probing component superblocks, deriving array identity, selecting a stable `/dev/md/` path, writing the map, and triggering sysfs change uevents for active arrays.

## Rebuild Logic

`RebuildMap()` reads `/proc/mdstat`, opens component devices from sysfs, guesses and loads superblocks, resolves subarray information for external metadata, obtains mdinfo, and chooses a path. It prefers existing `/dev/md/` mappings, then matching `mdadm.conf` identities, then metadata names adjusted by homehost, uniqueness checks, and numeric suffixes. It writes the rebuilt map once and emits uevents only if writing succeeded.

## Dependencies

This file integrates mdstat parsing, sysfs reads, superblock probing, mdadm config matching, homehost policy, device-number mapping, `/dev` path discovery, and metadata handler callbacks.

## Important Invariants

- Writers use `.new` plus `rename()` for atomic replacement.
- The lock file is unlinked before close by the lock owner.
- Bad/stale entries are skipped on write, allowing lookups to lazily prune dead mappings.
- `map_read()` attempts `RebuildMap()` if the map cannot be opened.
- Path conflict detection checks both filesystem state and existing map names.

## Risks

The map is runtime state, not authoritative metadata. It can be stale, missing, or rebuilt from incomplete system state. Naming decisions depend on homehost policy and mdadm.conf matching, so changes in config parsing can affect udev-visible array names.
