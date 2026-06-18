# File Research: sources/block-storage/lvm2/lib/metadata/metadata-exported.h

Purpose: defines LVM2's exported metadata model and large public-internal API surface for PV/VG/LV metadata, flags, segment structures, creation/resize parameters, pool/cache/raid/integrity/vdo operations, activation modes, and validation helpers.

Read coverage: complete file read, 1,507 lines.

Key contents:
- Defines sector, stripe, extent, and historical-LV constants.
- Defines extensive VG/PV/LV status flags, including visible/read/write, snapshot, pvmove, lock, mirror, RAID, thin, cache, writecache, integrity, VDO, pending-delete, reshape, metadata-format, activation-skip, and derived partial state.
- Defines format feature flags, mirror conversion flags, VG read flags, and VG read failure flags.
- Provides LV type macros for thin, mirror, RAID, cache, pool, writecache, integrity, VDO, removed, component, virtual, partial, and snapshot/origin state.
- Defines key enums: area type, force/prompt level, thin zero/discards/crop metadata, cache mode, cache metadata format, lock type, and activation change.
- Defines metadata container structures: `format_type`, `format_instance`, `pv_segment`, `lv_segment_area`, `lv_thin_message`, `lv_segment`, `pe_range`, `pv_list`, `glv_list`, `vg_list`, and `vgnameid_list`.
- `struct lv_segment` is the central per-segment model with generic geometry plus fields for mirror/RAID, snapshot, thin, pool, cache, writecache, integrity, and VDO targets.
- Defines PV creation and pvcreate parameter structures, LV resize parameters, wipe parameters, VDO conversion parameters, LV creation parameters, VG creation parameters, LV removal parameters, and status structs for thin, snapshot, RAID, cache, and VDO.
- Declares VG/PV lifecycle APIs: read, write, commit, revert, create, remove, rename, extend, split metadata areas, move PVs, validate names, validate VGs, orphan handling, PV resize/analyze/write, and system-id/foreign checks.
- Declares LV lifecycle APIs: create, extend, resize, remove, rename, update/reload, wipe, activate/wipe, layer insertion/removal, tag changes, pool metadata handling, and activation skip handling.
- Declares thin-pool, cache, VDO, mirror, RAID, writecache, snapshot, pvmove, integrity, and reporting helper APIs.

Dependencies:
- Includes ID, PV, VG, LV, percent, and lvmlockd headers plus `<stdbool.h>`.
- Used across lib metadata, tools, activation, daemon polling, segment-type handlers, and exported library-facing code.

Risk and edge cases:
- Many status bits are shared between object classes or reused for historical compatibility, so callers must interpret them in the right PV/VG/LV context.
- `struct lv_segment` is a cross-target union-like structure without an explicit union; validation must ensure fields for unrelated target types remain unset.
- Macros such as `lv_is_component()` depend on helper functions and flag combinations, so they can have non-obvious side effects or evaluation costs.
- This header is a broad contract: changing flags, structures, or prototypes can ripple across the whole metadata layer, tools, and reporting code.
- Fixed-size fields such as devicesfile in polling params and names in creation code require callers to preserve upstream validation and length limits.
