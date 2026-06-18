# File Research: sources/block-storage/lvm2/lib/metadata/segtype.h

This header defines LVM segment-type flags, canonical segment-type names, predicate macros, the `struct segment_type` object, the `struct segtype_handler` vtable, initialization prototypes, and target feature bits.

Major definitions:
- Generic segment flags include split support, striped/mirrored areas, snapshot, virtual, monitored, raid, thin, cache, mirror, writecache, integrity, VDO, and unknown types.
- RAID flags cover `raid0`, `raid0_meta`, `raid1`, `raid10_near`, `raid4`, all RAID5 layout variants, and all RAID6 layout variants.
- Name constants define stable strings such as `linear`, `striped`, `mirror`, `snapshot`, `thin-pool`, `cache`, `raid5_ls`, `raid6_zr`, `vdo-pool`, and others.
- Predicate macros classify segment types and segments, for example `segtype_is_raid()`, `segtype_is_any_raid5()`, `seg_is_raid_with_meta()`, `seg_is_reshapable_raid()`, `seg_is_thin_pool()`, and `segtype_supports_stripe_size()`.

Key structures:
- `struct segment_type` stores list linkage, flags, parity-device count, handler operations, name, DSO name, loaded library pointer, and private handler data.
- `struct segtype_handler` defines operations for naming, target naming, display, text import/export, segment merge, dm target line construction, status/percent parsing, target presence checks, module requirements, monitoring, and cleanup.

Feature flags:
- RAID feature flags describe dm-raid target capabilities such as RAID10, RAID0, reshaping, RAID4, shrink, reshape, and accepting rebuild args with empty metadata.
- Thin, VDO, cache, snapshot, and mirror feature flags describe target-specific capabilities used by their segment handlers.

Design role:
- This header is the central classification contract for metadata code. Files such as `raid_manip.c` depend on these macros to choose conversion paths, validate supported operations, and decide whether a segment has metadata, parity, striping, mirroring, or reshape support.
