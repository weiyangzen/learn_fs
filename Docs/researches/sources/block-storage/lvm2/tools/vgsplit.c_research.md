# File Research: sources/block-storage/lvm2/tools/vgsplit.c

Purpose: implements `vgsplit`, moving selected PVs or an LV’s used PVs from one VG into a new or existing destination VG while preserving LV stack consistency.

Read coverage: complete file read, 791 lines.

Key responsibilities:
- Validates source/destination VG names and that either PV paths or one LV name is supplied.
- Creates a new destination VG or reads an existing compatible one; rejects shared VGs.
- Applies new VG options only when creating a new VG, using defaults derived from the source VG.
- Archives the source VG before mutation, moves selected PVs, and optionally moves PVs used by a named LV.
- Recursively moves complete LV stacks between VGs with type-specific consistency checks.
- Handles standard LVs, snapshots, mirrors, RAID, thin pools/volumes/external origins, VDO pools/volumes, cache pools/cachevols/writecache, and pool metadata spare.
- Splits metadata areas and ensures metadata remains available when required.
- Writes destination VG as exported first, writes source VG, then clears exported flag and rewrites destination VG to support crash recovery.
- Coordinates persistent reservation start/stop for moved devices when PR settings differ between source and destination.

Dependencies:
- Uses VG create/read/update helpers, PV move helpers, LV relationship/type helpers, metadata area splitting, pool metadata spare handling, archive/backup, persistent reservation helpers, and lock handling.

Risks and edge cases:
- Many LV types cannot be split across VGs unless all dependent components move together.
- Active LVs cannot be moved; hidden/internal LVs are moved recursively with parents.
- Destination VG is written exported first as an explicit crash recovery strategy.
- Release order matters because the destination VG references elements moved from the source VG.
