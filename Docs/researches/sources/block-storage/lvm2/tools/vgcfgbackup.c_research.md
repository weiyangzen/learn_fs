# File Research: sources/block-storage/lvm2/tools/vgcfgbackup.c

Purpose: implements `vgcfgbackup`, writing VG metadata backups either through the normal backup mechanism or to an explicit user-specified file/template.

Read coverage: complete file read, 109 lines.

Key responsibilities:
- Expands the `--file` template with the VG name unless running under `security_level()`, where the template is copied literally.
- Prevents multiple VGs from being backed up to the same explicit filename by tracking the last expanded filename.
- For explicit files, calls `backup_to_file()` with the current command line and VG metadata.
- Without explicit file, refuses backup for VGs with missing PVs or unknown segments so the user must choose an explicit target.
- Forces normal backup generation with `backup_enable(cmd, 1)` before calling `backup(vg)`.
- Processes each selected VG through a `processing_handle` carrying the last filename buffer.

Dependencies:
- Uses tool argument APIs, `process_each_vg()`, archiver backup functions, missing-PV and unknown-segment VG checks.

Risks and edge cases:
- Filename template formatting is intentionally disabled at elevated security level.
- The repeated-filename guard compares only against the previous VG, matching sequential processing behavior.
- Missing PVs and unknown segments require `-f` to avoid silently creating normal backups from questionable metadata.
