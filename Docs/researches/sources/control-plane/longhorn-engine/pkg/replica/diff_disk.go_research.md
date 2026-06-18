# sources/control-plane/longhorn-engine/pkg/replica/diff_disk.go

Purpose: implements Longhorn's layered differencing disk read/write/unmap logic over a chain of sparse disk files.

Important APIs/types/functions: `diffDisk` stores a sector-to-file `location` cache, ordered `files`, `sectorSize`, `size`, and `rmLock`. `WriteAt` handles aligned writes directly and unaligned writes through read-modify-write. `fullWriteAt` writes to the active head and marks locations as the newest file. `ReadAt` and `fullReadAt` resolve sectors across files and coalesce reads by target. `lookup` discovers unknown sectors using FIEMAP from newest layer toward the base. `UnmapAt` trims sector-aligned ranges across the head and contiguous removed parent snapshots. `Expand`, `RemoveIndex`, `initializeSectorLocation`, and `preload` maintain location/files state.

Control flow: unaligned writes read the whole affected sector, modify the caller's byte range, and write the full sector to the active head. Reads split unaligned boundaries into sector-aligned reads. `lookup` treats file index 1 as the guaranteed base/backing layer if no newer file has an extent. `read` pads zeros when a disk is shorter than the volume and returns `io.ErrUnexpectedEOF` only past volume size.

State and persistence: `location` is an in-memory cache; writes/unmaps persist to underlying sparse files. `RemoveIndex` closes and removes a layer from the chain and rewrites cached indexes.

Dependencies and integration points: used by `Replica` for all data IO. Depends on `types.DiffDisk`, `go-fibmap`, sparse file semantics, and disk utility helpers.

Risks: `fullWriteAt` marks all sectors as written even if the underlying write returns a partial count/error. `lookup` depends on FIEMAP support and does not lock around location updates in read paths. `location` is byte-indexed, limiting practical chain indexes to 255. Unmap returns actual-size reduction, not requested length, and may return zero if size accounting fails even after successful unmap. Overflow and bounds around `location[startSector+i]` rely on callers not writing beyond volume.

Test signals: `diff_disk_test.go` covers aligned/unaligned writes and nominal partial-write byte accounting. `replica_test.go` covers read/write, partial IO, unmap alignment, backing file shorter than volume, and reload reconstruction.
