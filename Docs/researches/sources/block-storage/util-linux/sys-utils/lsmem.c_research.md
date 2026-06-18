# File Research: sources/block-storage/util-linux/sys-utils/lsmem.c

`lsmem.c` implements `lsmem(1)`, which reports Linux memory block ranges, online/offline state, removability, NUMA node, zones, firmware memory configuration, and summary totals.

Key behavior:
- Reads memory block data from `/sys/devices/system/memory`.
- Optionally reads configured and memmap-on-memory state from `/sys/firmware/memory`.
- Supports table, summary, summary-only, JSON, raw, pairs/export, bytes, sysroot, all-blocks, custom columns, split policy, and annotated headers.
- Groups adjacent memory blocks into ranges unless `--all` is used or selected split fields differ.
- Default columns are range, size, state, removable, and block.
- Can split ranges by state, node, removable flag, zones, firmware configuration, and memmap-on-memory.
- Reads memory block size from `block_size_bytes`.
- Detects NUMA node membership by scanning `memoryN/nodeX` entries.
- Detects zone support through `valid_zones` and parses zone names.
- Computes online/offline memory totals while reading blocks.
- Prints memory hotplug `memmap_on_memory` module parameter when available.

Important dependencies:
- `path_cxt` for sysfs and sysroot-safe path access.
- `libsmartcols` for table/JSON/raw/export output.
- util-linux size formatting, option exclusivity, annotation, and allocation helpers.

Risk notes:
- The firmware memory configuration tree is optional and columns are skipped when unavailable.
- Summary-only mode returns early without freeing path contexts, relying on process exit cleanup.
- Block merging depends on sorted `versionsort()` directory results and contiguous block indices.
- `read_info()` counts each memory config directory as one block-size unit for totals, even when firmware config is used as the iteration source.
