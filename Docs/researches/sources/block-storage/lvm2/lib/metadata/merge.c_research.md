# File Research: sources/block-storage/lvm2/lib/metadata/merge.c

Purpose: implements LV segment merging, segment splitting, and deep metadata consistency validation for LV segment graphs across striped, mirrored, RAID, thin, cache, VDO, integrity, snapshot, pvmove, and pool layouts.

Read coverage: complete file read, 1,049 lines.

Key responsibilities:
- Merges adjacent compatible segments through segment-type `merge_segments` callbacks while avoiding pvmove and locked LV structures.
- Defines bounded validation error accumulation to avoid unbounded error storms.
- Performs RAID-specific validation for raid0, raid1, raid4/5/6/10, including area counts, metadata areas, stripe size, region size, recovery-rate ordering, data offsets, reshape flags, image/meta LV flags, size consistency, and visibility rules.
- Validates cache segments: cache LV flags, pool/cachevol references, metadata format, mode, policy name/settings, chunk size, and metadata-format flag consistency.
- Validates mirror logs, mirror image back references, mirror region size, and mirrored image sizing.
- Validates pool segments for one data LV, metadata LV presence, and bidirectional references.
- Validates thin pool and thin volume fields, including chunk size, zero/discard/crop settings, transaction IDs, pool references, device IDs, external origins, and merge LV flags.
- Validates VDO pool and VDO LV fields and target parameters.
- Validates integrity segments and `_iorig` naming/relationship expectations.
- Validates segment fields that must be unset for unrelated segment types, including pool LV, chunk size, transaction ID, VDO params, policy fields, and segtype-private storage.
- Checks complete VG metadata for single-segment type requirements, pool data back references, metadata LV naming suffixes, external-origin counts, and read-only requirements.
- Checks incomplete VG metadata for consecutive/non-overlapping segments, LE count consistency, PV segment back references, LV `segs_using_this_lv` references, reference counts, and historical indirect-origin links.
- Splits a segment at a requested logical extent by cloning the segment, copying tags, adjusting lengths/LEs/area offsets, and reassigning PV or LV areas.

Important entry points:
- `lv_merge_segments()`.
- `check_lv_segments_complete_vg()`.
- `check_lv_segments_incomplete_vg()`.
- `lv_split_segment()`.

Dependencies:
- Uses metadata, defaults, LV allocation, PV allocation, string lists, segment-type helpers, display helpers, VDO validation, thin/cache chunk validators, and many LV flag helpers from `metadata-exported.h`.
- Relies on segment-type operation callbacks for merge and split capability.

Risk and edge cases:
- Validation encodes many metadata invariants; changing LV status flags or segment fields requires updating these checks.
- RAID reshape states intentionally relax or alter some constraints, especially data offsets and health/count matching.
- Segment splitting must update PV segment ownership or LV area LE offsets exactly, or later allocation and validation will see inconsistent graphs.
- `ERROR_MAX` limits diagnostics to 100 errors, so severe corruption may produce truncated validation output.
