# File Research: sources/block-storage/lvm2/tools/vgmerge.c

Purpose: implements `vgmerge`, merging one or more source VGs into a target VG.

Read coverage: complete file read, 271 lines.

Key responsibilities:
- Takes global exclusive lock, clears hints, and merges each source VG into the target.
- Locks/read VGs in name order to reduce lock ordering conflicts.
- Rejects shared VGs and requires source VG LVs to be inactive.
- Validates VG compatibility and equal persistent reservation settings.
- Handles duplicate pool metadata spare LVs by removing the smaller spare and rechecking compatibility.
- Archives both VGs before mutation.
- Moves PVs, metadata areas, and LVs from source to target, updates PV VG names/status, updates LV VG association and LVID VG component, and regenerates colliding LV UUID components.
- Updates extent/free counts, old-name tracking, pool metadata spare sizing, writes/commits the target VG, and creates a backup.

Dependencies:
- Uses VG read-for-update, compatibility checks, archive/backup, LV/PV list manipulation, ID generation, pool metadata spare handling, and metadata area list movement.

Risks and edge cases:
- Release order matters because the target VG references moved structures from the source VG.
- LVID collisions are resolved only for matching second ID components against existing target LVs.
- The source VG’s `/dev` directory removal is noted as FIXME.
