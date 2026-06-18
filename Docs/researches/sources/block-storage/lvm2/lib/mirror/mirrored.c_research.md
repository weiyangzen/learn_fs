# File Research: sources/block-storage/lvm2/lib/mirror/mirrored.c

This file defines the classic device-mapper mirror segment type plugin/handler.

Main entry points:
- Segment operations through `_mirrored_ops`: display, text import/export, target line generation, target percent, target presence, transient status, modules needed, dmeventd monitor hooks, destroy.
- Initialization: `init_mirrored_segtype()` or shared `init_segtype()`.

Behavior:
- Text import reads `mirror_count`, optional `extents_moved`, `region_size`, `mirror_log`, and `mirrors`.
- Text export writes mirror count, pvmove progress, mirror log, region size, and areas.
- `_mirrored_add_target_line()` handles normal mirrors and pvmove mirrors. Pvmove segments before current copy use the second area, after current copy use a linear first area, and only one segment runs as mirror at once.
- `_add_log()` chooses disk log or core log, sets `DM_CORELOG`, `DM_NOSYNC`, and optionally block-on-error/handle-errors behavior when monitoring is present.
- `_mirrored_target_percent()` parses mirror status and updates `extents_copied`.
- `_mirrored_transient_status()` compares kernel mirror devices/logs with metadata, marks failed legs/logs as `PARTIAL_LV`, and updates VG partial state.

Dependencies:
- Device-mapper mirror target, target version probing, dmeventd monitor library, text import/export helpers, activation info, and segment module lists.

Correctness notes:
- Disk log metadata must match the active kernel log device.
- Region size is required for logged mirrors.
- Block-on-error support is version-gated and warnings are suppressed after first print.
- `mirror_in_sync()` can set `DM_NOSYNC` for non-pvmove mirrors.

Risks:
- Classic mirror code must reconcile metadata and live kernel state; mismatches are treated as errors.
- Pvmove behavior depends on `extents_copied` and `pvmove_mirror_count` sequencing across segments.
