# sources/cloud-native/nydus/smoke/tests/overlay_fs_test.go

## Purpose
This suite verifies Nydus writable overlay configuration by mounting a RAFS lower layer with an overlay upper/work directory, writing through the mount, and confirming the new file lands in the upperdir.

## Important APIs, Types, And Functions
`OverlayFsTestSuite.prepareTestEnv` creates a default context, packs a lower texture layer, merges it with `OCIRef=true`, verifies the read-only lower mount, and returns the context. `TestSimpleOverlayFs` builds a `tool.NydusdConfig` with overlay upper/work dirs and `Writable=true`, mounts, writes `test.txt` under the mount, reads it back through the mount, then reads the same file directly from `ctx.Env.OvlUpperDir`.

## Control Flow
The test first proves the lower image is valid through a normal mount. It then starts a writable overlay Nydus mount, writes a file through FUSE, verifies read-after-write via FUSE, and checks upperdir persistence.

## State And Persistence
Temporary workdir state includes lower source, blobs, bootstrap, cache, mount, overlay upper, and overlay work directories. The file `test.txt` is expected to persist in the upperdir after it is written through the mount.

## Dependencies And Integration Points
This integrates `tool.NewNydusdWithOverlay`, the overlay-specific config template in `tool/nydusd.go`, `snapshotter-converter`, and kernel overlay/FUSE behavior. It also uses `containerd/log` for deferred unmount logging.

## Risks
Writable overlay behavior requires host permissions and compatible kernel features. The preliminary lower verification adds time but helps isolate pack/merge issues from overlay failures. The test covers file creation but not deletion, rename, whiteout, or metadata mutation through the writable mount.

## Test Signals
The key signals are successful writable mount, exact `hello world` read through the mount, and identical content in the upperdir backing file.
