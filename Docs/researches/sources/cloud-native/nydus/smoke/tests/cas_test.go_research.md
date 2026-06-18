# sources/cloud-native/nydus/smoke/tests/cas_test.go

## Purpose
This Go smoke-test suite validates the Nydus chunk deduplication/CAS SQLite database side effects while mounting RAFS images with `nydusd`. It verifies both direct daemon startup with a dedup DB and API-driven submount lifecycle cleanup, with prefetch enabled and disabled.

## Important APIs, Types, And Functions
`CasTestSuite` exposes two dynamic suite generators. `TestCasTables` iterates `enable_prefetch=false,true` and calls `testCasTables`; `TestCasGcUmountByAPI` uses the same dimension and calls `testCasGcUmountByAPI`. `testCasTables` uses `texture.PrepareLayerWithContext`, sets `ctx.Runtime.ChunkDedupDb`, mounts through `tool.NewNydusdWithContext`, verifies the mounted tree, opens SQLite, checkpoints WAL, and asserts `Blobs` has one row and `Chunks` reaches thirteen rows. `testCasGcUmountByAPI` starts a generic `nydusd`, mounts an image through `/api/v1/mount`, verifies at a subpath, checks nonzero CAS rows, deletes the cache directory to mimic snapshotter cache cleanup, unmounts by API, and requires the CAS tables to be empty.

## Control Flow
The test flow is build synthetic texture layer, configure dedup DB path, run daemon, mount, walk/compare files, inspect DB, then unmount. The API GC variant first starts `nydusd` without a bootstrap, constructs the full per-mount config after the daemon is running, mounts `/mount` by API, then tests cleanup after `DELETE /api/v1/mount`.

## State And Persistence
The central persistent artifact is `cas.db` under the test work directory. It uses SQLite WAL behavior, so tests issue `PRAGMA wal_checkpoint(FULL)` before reads. The API GC test deletes `cache/` before unmount to simulate external snapshotter state loss and expects Nydus CAS tables to be garbage-collected on API unmount.

## Dependencies And Integration Points
This depends on `github.com/mattn/go-sqlite3`, `texture` layer builders, `tool.Nydusd`, and the local `nydusd` API socket. It also relies on Nydus creating tables named `Blobs` and `Chunks`, so schema naming is an integration contract with daemon-side CAS code.

## Risks
The fixed chunk count of thirteen is tightly coupled to the synthetic texture layer and packing behavior. Chunk insertion can lag behind filesystem reads, so the polling loop protects only `Chunks` in the direct mount test. The tests require working FUSE, SQLite driver availability, and sufficient privileges for the texture layer.

## Test Signals
Success signals include exact or nonzero CAS row counts, zero file-tree mismatches from `nydusd.Verify`, and zero rows after API unmount cleanup. Failures identify regressions in CAS population, WAL visibility, API submount cleanup, prefetch interaction, or file-serving correctness.
