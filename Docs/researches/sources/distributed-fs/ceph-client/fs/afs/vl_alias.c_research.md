<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/vl_alias.c -->
# sources/distributed-fs/ceph-client/fs/afs/vl_alias.c

## Purpose
Detects when an AFS cell is an alias of another known cell and selects the canonical/master cell for mounts.

## Important APIs, Types, And Functions
Exports `afs_cell_detect_alias()`. Internal helpers sample volumes, compare fileserver address lists, compare volume server lists, compare `root.cell`, query existing cells for known volumes, request YFS canonical cell names, and perform the full alias detection workflow.

## Control Flow
Alias detection is serialized by `cells_alias_lock`. It first asks YFS VL servers for a canonical cell name; if different, it looks up that cell and records `alias_of`. If unsupported, it samples `root.cell` and compares volume IDs, server UUIDs, and shared endpoint peers with existing cells. If no root volume exists, it samples another known volume from existing cells.

## State And Persistence
Mutates `cell->alias_of`, `cell->root_volume`, and clears `AFS_CELL_FL_CHECK_ALIAS` on successful detection. Sampled volumes and cells are refcounted. Alias knowledge is memory-only per net namespace.

## Dependencies And Integration Points
Depends on VL server rotation, YFS VL client canonical-name RPC, volume creation, cell lookup, volume/server lists, endpoint state, proc cell list, and mount validation in `super.c`.

## Risks And Edge Cases
Alias detection is heuristic when canonical names are unavailable. Cells sharing some VL/fileserver endpoints or volumes can be ambiguous. Interruptible locking can fail. Comparing endpoint peers assumes address lists are current and sorted compatibly.

## Test Signals
YFS canonical cell aliases, DNS aliases pointing at the same VL servers, cells with shared `root.cell`, cells without `root.cell` but shared volumes, unrelated cells with same volume names, and mount alias switching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/vl_alias.c -->
