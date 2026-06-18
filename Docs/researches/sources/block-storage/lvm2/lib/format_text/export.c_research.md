# File Research: sources/block-storage/lvm2/lib/format_text/export.c

This file serializes in-memory LVM volume group metadata into the text metadata format, either to a `FILE`, to a dynamically resized raw buffer, or to a parsed config tree. It also exposes formatter helpers used by segment-specific text exporters.

Formatter design:
- `struct formatter` stores output destination, indentation, header placement, comment behavior, newline/output callbacks, and a radix tree mapping PV pointers to stable `pvN` names.
- File output emits tab-indented lines with optional aligned comments. Raw output appends to a heap buffer and doubles the buffer as needed.
- `_init` caches `uname` data used in metadata headers.
- Public formatter helpers include `out_inc_indent`, `out_dec_indent`, `out_newline`, `out_size`, `out_hint`, `out_text_with_comment`, `out_text`, `out_config_node`, and `out_areas`.

Header and common field output:
- `_print_header` writes LVM version, contents marker, format version, escaped description, creation host/system_id, and creation time.
- `_print_flag_config` uses `print_flags` to emit `status` and compatible `flags` arrays.
- `_out_list` formats tag/other string lists.
- `_sectors_to_units` provides human-readable size comments for file output.

VG/PV/LV serialization:
- `_print_vg` writes VG id, seqno, informational format name, status/flags, tags, system_id, lock_type/lock_args, persistent reservation settings, extent size, max LV/PV counts, allocation policy, profile, and metadata copies.
- `_build_pv_idx` assigns PV pointer-to-index mappings, and `_get_pv_idx` resolves them while exporting segment areas.
- `_print_pvs` writes each `pvN` block with id, hint device name, device-id metadata, status/flags, tags, device size, PE start/count, and optional bootloader area.
- `_print_lv` writes each LV block with id, status/flags, tags, creation timestamp/host, lock args, allocation policy, profile, read ahead, persistent major/minor, segment count, and each segment block.
- `_print_segment` writes segment extent range, reshape count, type plus encoded segtype LV flags, segment tags, and delegates target-specific fields to `segtype->ops->text_export`.
- `_print_lvs` writes visible LVs before hidden/internal LVs.
- Historical LV support writes creation/removal times, origin references, and live descendant lists while omitting historical descendants from the descendant buffer.

Top-level exports:
- `_text_vg_export` builds the PV index, optionally writes the header before or after the VG block, writes the VG block and child sections, then destroys the PV radix tree.
- `text_vg_export_file` writes comment-rich metadata to a `FILE`.
- `text_vg_export_raw` writes compact metadata to a dynamically allocated buffer sized from `vg->buffer_size_hint + 16384`.
- `export_vg_to_config_tree` exports to a raw buffer and reparses it into a `dm_config_tree`.

Important invariants:
- PV references in segment areas are exported as `pvN` names derived from pointer identity for the current export pass.
- Raw exports set `header = 0`, so the header is written after the VG block.
- WRITE flags may be transformed to `LVM_WRITE_LOCKED` for old-version compatibility when the VG is write-locked.
- Output helpers return failure on allocation, formatting, radix tree, or target text-export errors, causing the whole export to fail.
