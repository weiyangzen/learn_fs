# sources/cloud-native/containers-storage/drivers/overlay/composefs.go

## Purpose
`composefs.go` supports overlay's composefs/EROFS additional-layer path. It generates composefs blobs with `mkcomposefs`, enables fs-verity when possible, opens EROFS filesystem mounts using the new mount API, and moves those mounts to target mountpoints.

## Important APIs, Types, And Functions
State includes cached `mkcomposefs` lookup fields and `skipMountViaFile`. Functions include `getComposeFsHelper`, `getComposefsBlob`, `generateComposeFsBlob`, `hasACL`, `openBlobFile`, `openComposefsMount`, and `mountComposefsBlob`.

## Control Flow
`generateComposeFsBlob` creates a composefs data directory, generates JSON dump data from TOC and verity digests, runs `mkcomposefs --from-file - -`, writes `composefs.blob`, reopens it read-only, and attempts fs-verity enablement. `openComposefsMount` reads ACL flags, tries mounting EROFS directly from the file, falls back to a readonly loop device on `ENOTBLK`, and caches that fallback. `mountComposefsBlob` moves the detached mount FD to the target path.

## State And Persistence
Persistent state is `composefs.blob` under the data directory. Runtime state caches helper lookup and whether direct file-backed EROFS mounting should be skipped. Loop devices and mount file descriptors are temporary resources.

## Dependencies And Integration Points
It integrates with overlay additional layer support and chunked composefs artifacts. Dependencies include `dump.GenerateDump`, `fsverity`, `loopback`, `unix` fsopen/fsconfig/fsmount/move_mount APIs, `mkcomposefs`, and logrus.

## Risks
Requires external `mkcomposefs`, kernel EROFS support, and newer mount APIs. Direct file mounting works only on newer kernels, so fallback logic must remain correct. Blob header flag parsing assumes the composefs/EROFS header layout. Failed fs-verity enablement is warning-only for unsupported ioctls.

## Test Signals
No direct tests in this subset. Overlay additional layer and composefs integration tests elsewhere would validate blob generation and mount behavior.
