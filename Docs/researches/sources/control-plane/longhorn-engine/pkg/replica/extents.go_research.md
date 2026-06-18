# sources/control-plane/longhorn-engine/pkg/replica/extents.go

Purpose: preloads a diff disk's sector location cache from filesystem extents using FIEMAP.

Important APIs/types/functions: `MaxExtentsBuffer` caps FIEMAP results at 1024 extents per call. `LoadDiffDiskLocationList` walks extents from a disk fd across the volume-sized logical range and marks every sector covered by each extent with `currentFileIndex`.

Control flow: the function repeatedly calls `fibmap.Fiemap` from the current logical start. It exits when no extents remain or when an extent has `FIEMAP_EXTENT_LAST`. For each extent, it advances in sector-size increments and updates `diffDisk.location`.

State and persistence: mutates only the in-memory location cache. It reads filesystem allocation state but does not write files.

Dependencies and integration points: called by `diffDisk.preload`, which is used by backup comparison and data layout export. Depends on `types.DiffDisk.Fd()` returning a valid fd and `go-fibmap`.

Risks: assumes extents align sufficiently with replica sector accounting; partial-sector extents are rounded through integer division. No explicit bounds check is performed before indexing `location`, so inconsistent FIEMAP ranges could panic. Filesystems without FIEMAP support fail replica preload-dependent operations.

Test signals: no direct tests here. Backup and reload tests indirectly depend on location preloading.
