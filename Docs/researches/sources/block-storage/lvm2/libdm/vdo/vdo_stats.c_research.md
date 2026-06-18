# File Research: sources/block-storage/lvm2/libdm/vdo/vdo_stats.c

Purpose: parses VDO kernel stats message strings into structured `dm_vdo_stats` data and, optionally, a flat list of label/value fields.

Read coverage: complete file read, 254 lines.

Key responsibilities:
- Parses nested VDO stats of the form `{ key : value, key : { nested : value } }`.
- Builds readable labels by joining nesting prefixes and converting camel-case keys to spaced labels.
- Recognizes selected labels and fills known `dm_vdo_stats` fields such as data/overhead/logical blocks, physical/logical block counts, block sizes, write bios, and operating mode.
- Optionally records up to `MAX_STATS` label/value pairs in `dm_vdo_stats_full.fields`.
- Allocates a single contiguous result containing `dm_vdo_stats_full`, optional field array, and `dm_vdo_stats`.

Important entry point:
- `dm_vdo_stats_parse(struct dm_pool *mem, const char *stats_str, unsigned flags)`

Dependencies:
- Uses `libdm/misc/dmlib.h`, public `libdm/libdevmapper.h` VDO stats structures, and helpers from `vdo/vdo_parse.h`.

Risk and edge cases:
- The parser is permissive: malformed sections generally stop traversal rather than returning an explicit parse error.
- Nesting deeper than 16 levels returns the end pointer and stops normal parsing.
- Full field collection is capped at 250 entries.
- Unknown fields are still preserved in full mode but ignored by structured stats extraction.
- If `DM_VDO_STATS_FULL` is not set, `field_count` is forced back to zero before return.
