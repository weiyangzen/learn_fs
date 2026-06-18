# File Research: sources/block-storage/lvm2/tools/vgreduce.c

Purpose: implements `vgreduce`, removing PVs from a VG or repairing a VG by removing missing PVs and partial LVs.

Read coverage: complete file read, 284 lines.

Key responsibilities:
- Validates command-line combinations for normal PV removal versus `--removemissing` repair mode.
- Normal mode processes selected PVs and calls metadata-layer `vgreduce_single()` after write/resize status checks.
- Repair mode enables missing-PV handling and ignores suspended devices while making the VG consistent.
- Removes empty missing PVs and warns about remaining partial LVs.
- With force, recursively removes missing RAID legs, mirror images, or whole partial visible LVs and restarts scanning after each mutation.
- Honors `--mirrorsonly` by rejecting removal of non-mirrored partial visible LVs.
- Writes and commits a consistent VG, reporting already-consistent, fixed, or failed state.

Dependencies:
- Uses VG/PV processing, RAID missing-leg removal, mirror missing removal, LV dependency removal, VG write/commit, partial LV marking, and ignore-suspended-device control.

Risks and edge cases:
- VG must always retain at least one PV.
- Without force, repair may only remove empty missing PVs and fail if partial LVs remain.
- Forced repair can remove user-visible partial LVs and their dependencies.
