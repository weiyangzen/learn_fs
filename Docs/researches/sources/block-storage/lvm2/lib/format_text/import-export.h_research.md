# File Research: sources/block-storage/lvm2/lib/format_text/import-export.h

## Summary
Defines the shared text metadata import/export contract, format-version dispatch table, flag conversion APIs, and metadata read/export entry points.

## Main Contents
- Text metadata identity fields: `contents = "Text Format Volume Group"` and `version = 1`.
- `enum pv_vg_lv_e` distinguishes PV, VG, and LV flag namespaces.
- Flag masks distinguish compatible flags, status flags, and segment-type/LV flags.
- `struct text_vg_version_ops` supplies version-specific `check_version`, `read_vg`, `read_desc`, and `read_vgsummary` callbacks.

## Key APIs
Declares version-1 initialization, flag printing/reading, LV flag parsing, file/raw export, full metadata read, metadata-file read, and metadata-summary read.

## Risks And Invariants
Import dispatch assumes version handlers can reject incompatible config trees cleanly. Summary reads and full reads share checksum and wraparound parameters, so callers must pass consistent raw MDA location data.
