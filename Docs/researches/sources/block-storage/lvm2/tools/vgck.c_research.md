# File Research: sources/block-storage/lvm2/tools/vgck.c

Purpose: implements `vgck`, validating VG metadata and optionally rewriting metadata to repair/update metadata areas.

Read coverage: complete file read, 108 lines.

Key responsibilities:
- Normal mode validates the VG with `vg_validate()` and fails if any PVs are missing.
- `--updatemetadata` mode enables missing-PV/unknown-segment handling and outdated-PV wiping, then rewrites VG metadata.
- Uses `vg_write()`/`vg_commit()` to clean metadata inconsistencies such as old MDA versions, outdated PVs, PV header flags, historical LVs, and unused missing-PV flags.
- Preserves the text metadata buffer across commit so `vg_write_commit_bad_mdas()` can write the same metadata to bad metadata areas.
- Frees preserved text metadata after attempting bad-MDA repair.

Dependencies:
- Uses format-text metadata helpers, VG validation/write/commit APIs, lvmcache bad-MDA tracking, and process-each-VG framework.

Risks and edge cases:
- Comments explicitly state some corruptions remain unrepaired: label header, PV header/locations, and some MDA header fields.
- `--updatemetadata` can write to VGs with missing PVs or unknown segments, so it is broader than simple validation.
