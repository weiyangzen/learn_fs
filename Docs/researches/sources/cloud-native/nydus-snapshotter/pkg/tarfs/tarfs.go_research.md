<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/tarfs/tarfs.go -->
## sources/cloud-native/nydus-snapshotter/pkg/tarfs/tarfs.go

Purpose: manages tarfs conversion and mounting for ordinary OCI layers. It downloads layer blobs, converts tar streams into nydus tarfs bootstraps/data, merges layers into an image bootstrap, optionally exports block-device images with dm-verity labels, and mounts EROFS on the host.

Important APIs/types: `Manager`, `snapshotStatus`, status constants, artifact name constants, `NewManager`, image metadata fetchers, `PrepareLayer`, `MergeLayers`, `ExportBlockData`, `MountTarErofs`, `UmountTarErofs`, `DetachLayer`, `CheckTarfsHintAnnotation`, `GetConcurrentLimiter`, and path helpers. State is tracked by `snapshotMap` keyed by snapshot ID; each status holds conversion state, blob ID/path, loop devices, EROFS mountpoint, waitgroup, and cancel function.

Control flow and persistence: `PrepareLayer` registers a preparing status and launches `blobProcess`. `blobProcess` resolves credentials, fetches the compressed blob by digest, decompresses it, optionally validates diffID from manifest/config, streams it through `generateBootstrap`, and marks status ready/failed. `generateBootstrap` uses a FIFO plus `io.TeeReader` so `nydus-image create --type tar-tarfs` consumes the tar stream while the raw tar is cached. `MergeLayers` waits for parent layers, orders bootstraps low-to-high, and runs `nydus-image merge`. `ExportBlockData` runs `nydus-image export --block`, parses dm-verity output, and mutates snapshot labels. `MountTarErofs` attaches tar/bootstrap files to loop devices, mounts EROFS, and annotates the RAFS object.

Dependencies/integration: integrates with registry remote/auth code, containerd compression/storage labels, config tarfs flags, `nydus-image`, Linux FIFO/mount/loopdev APIs, lru caches, singleflight, and filesystem/snapshot flows.

Risks and test signals: high operational risk: external binary execution, parsing CLI stdout, async goroutine failures, loop-device lifecycle, and host mount privileges. `blobProcess` returns early after starting a goroutine, so readiness must always be observed via waitgroup/status. No direct tests in this subset; snapshotter paths exercise it indirectly when tarfs is enabled.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/tarfs/tarfs.go -->
