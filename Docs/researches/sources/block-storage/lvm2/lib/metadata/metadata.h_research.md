# File Research: sources/block-storage/lvm2/lib/metadata/metadata.h

## Purpose

`metadata.h` defines the internal metadata contracts shared across LVM2 metadata modules. It exposes format/MDA operation tables, format-instance state, metadata-area flags and error bits, segment access macros, small list wrapper types, format handler callbacks, and declarations for core VG/PV/LV metadata helpers implemented across `metadata.c`, `lv_manip.c`, `mirror.c`, `pool_manip.c`, thin manipulation, and PV accessors.

## Key Contents

- Constants and macros: `MIN_PE_SIZE`, `MAX_PE_SIZE`, `MIRROR_LOG_OFFSET`, `VG_MEMPOOL_CHUNK`, `dm_div_up()`, `dm_round_up()`, temporary postorder flags, `SHARED`, `FMT_PRECOMMIT`, MDA status bits, primary-MDA IO reasons, and `BAD_MDA_*` read/repair flags.
- `struct metadata_area_ops`: per-MDA callbacks for VG read/precommit-read, write, precommit, commit, revert, remove, metadata-location copy/name/offset, free/total sectors, membership check, PV MDA analysis, location comparison, device lookup, and config import/export.
- `struct metadata_area`: per-location state including ops pointer, opaque location, status, header start, scan-time text offset/checksum, MDA number, detected bad fields, and fields to suppress during repair.
- `struct format_instance_ctx` and `alloc_fid()`: describe and allocate format instances for a PV or VG reference.
- `struct format_handler`: per-format callbacks for scan, PV read/init/setup/add/remove/resize/write/rewrite check, LV/VG setup, segment support, format instance creation/destruction, and format destruction.
- Segment access macros: `seg_pvseg()`, `seg_dev()`, `seg_pe()`, `seg_le()`, and `seg_metale()`.
- Lightweight list records: `name_list`, `mda_list`, `peg_list`, and `seg_list`.

## Exposed API Surface

- Core metadata utilities: default PV metadata sizing, PE alignment, PV/device size checks, VG status checks, PV addition, LV/PV lookup, segment lookup, LV segment validation/merge/split, LV dependency reverse-link management, sub-LV traversal, segment movement, and readahead calculation.
- Metadata import/export: `export_vg_to_config_tree()`, `import_vg_from_config_tree()`, and `vg_from_config_tree()`.
- Mirror and pool hooks: mirror import fixup; pool attach/detach/create/spare sizing; thin-pool message and metadata sizing functions.
- Library-facing PV accessors: `pv_id()`, `pv_format_type()`, and `pv_vg_id()`.
- MDA/FID helpers: add/remove/index MDA, copy MDA, compare MDA locations, get MDA device, set/get ignored state, and set PV/VG format instances with reference counting.

## Design Notes

- The header separates format-independent metadata graph operations from format-specific disk layout through callback tables. `metadata.c` and format modules communicate through `metadata_area_ops` and `format_handler`.
- Comments emphasize that `format_instance` must be assigned only through `pv_set_fid()` and `vg_set_fid()` because the reference count and destructor behavior are centralized there.
- MDA state is intentionally not owned directly by a PV. The same abstraction can describe raw disk MDAs, file MDAs, or cached scan locations, and the owning list changes between lvmcache and VG format instances.

## Dependencies

The header includes device-cache, LVM string helpers, and `metadata-exported.h`, and it declares types from config trees, lvmcache, format metadata, allocation, devices, logical volumes, physical volumes, and command contexts.

## Risks And Edge Cases

- Many macros directly dereference segment area arrays and assume callers have already validated area type and bounds.
- `BAD_MDA_*` flags are low-level repair policy inputs; misclassifying a bad field can cause either missed repair or unsafe metadata overwrite.
- `format_handler` documents that `vg_write()` must not touch PVs outside the supplied VG, while noting format1 breaks this rule.
- Some declarations are intentionally cross-file internal APIs rather than stable library interfaces; misuse outside the expected metadata transaction flow can bypass validation or reverse-link maintenance.

## Summary

`metadata.h` is the internal ABI for LVM2's metadata subsystem. It defines how formats, metadata areas, PVs, VGs, LV segments, mirror code, pool code, and import/export code plug into the shared in-memory metadata model.
