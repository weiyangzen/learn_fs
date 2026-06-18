# File Research: sources/block-storage/util-linux/sys-utils/chmem.c

## Scope

Implements `chmem`, a sysfs-based memory hotplug/configuration utility for bringing memory blocks online/offline, configuring/deconfiguring memory ranges, selecting zones, and setting `memmap_on_memory`.

## Public And Internal APIs Covered

- Main command-line entry point.
- Online/offline by size or range: `chmem_onoff_size()`, `chmem_onoff_range()`.
- Configure/deconfigure by size or range: `chmem_config_size()`, `chmem_config_range()`, `chmem_config()`.
- Sysfs discovery: `read_info()`, `read_conf()`, `filter()`, `have_mem_blk_zones()`.
- Parameter parsing: `parse_parameter()`, `parse_single_param()`, `parse_range_param()`.
- Zone handling: `zone_name_to_id()`.

## Control Flow And Behavior

- Accepts exactly one action and one size/range/block-range argument.
- Supports byte/address ranges or memory block numbers via `--blocks`.
- Reads `/sys/devices/system/memory`, scans `memoryN` directories, and reads `block_size_bytes`.
- Optional `/sys/firmware/memory` support is used for configure/deconfigure and `memmap_on_memory`.
- Online operations can choose a zone:
  - `online_movable` for `Movable`.
  - `online_kernel` for other selected zones.
  - default online prefers `Movable` when valid.
- Disable/deconfigure operations iterate from high to low blocks for size-based requests; enable/configure iterate low to high.
- Range operations iterate matching memory block indexes and report total, partial, or failed completion.
- Verbose mode prints per-block actions using physical address ranges derived from block size.

## State And Data Structures

- `struct chmem_desc` holds path contexts, scanned memory and memconfig directories, block size, selected range/size, feature flags, zone state, and verbosity.
- Zone names include `DMA`, `DMA32`, `Normal`, `Highmem`, `Movable`, and `Device`.

## Dependencies

- util-linux sysfs path helpers, string-vector splitting, size parsing, option exclusion, allocation, and i18n helpers.
- Kernel sysfs memory attributes: `state`, `valid_zones`, `block_size_bytes`, optional firmware `config` and `memmap_on_memory`.

## Risks And Invariants

- Sizes and address ranges must align to memory block size.
- Disabling a block in a zone-aware system checks `valid_zones` and may reject zone mismatch.
- Configure/deconfigure paths require firmware memory config support; otherwise the utility tells users to use enable/disable.
- Partial success returns `64` (`CHMEM_EXIT_SOMEOK`).
- Directory scans and feature detection must stay consistent with the sysfs layout exposed by the running kernel or sysroot.
