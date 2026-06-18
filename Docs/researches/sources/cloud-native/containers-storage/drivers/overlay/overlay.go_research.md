<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlay/overlay.go -->
# sources/cloud-native/containers-storage/drivers/overlay/overlay.go

## Purpose
`overlay.go` is the Linux implementation of the overlay and overlay2 graph driver. It owns driver initialization, feature probing, overlay directory layout, layer creation/removal, mounting/unmounting, native and naive diff selection, ID-mapped mounts, composefs integration, additional read-only layer stores, project quota wiring, and deduplication over overlay layer `diff` directories.

## Important APIs, Types, And Functions
`overlayOptions` carries parsed driver settings: image stores, additional layer stores, project quota limits, mount program, mount options, force mask, chown behavior, and composefs. `Driver` stores `home`, `runhome`, optional `imageStore`, ref counter, quota controller, cached feature booleans, staging locks, and naive diff wrapper. `Init`, `parseOptions`, `SupportsNativeOverlay`, `supportsOverlay`, `Create`, `CreateReadWrite`, `Get`, `Put`, `Remove`, `Diff`, `ApplyDiff`, `Changes`, `UpdateLayerIDMap`, `LookupAdditionalLayer`, and `Dedup` form the main API surface. Helpers such as `cachedFeatureCheck`, `recreateSymlinks`, `redirectDiffIfAdditionalLayer`, and `getMergedDir` protect operational edge cases.

## Control Flow
`Init` parses options, identifies backing filesystem, creates `home/l`, optional image-store link directories, and `runhome`, then chooses native overlay or a `mount_program` such as `fuse-overlayfs`. Native mode probes d_type, multiple lower support, metacopy, volatile, data-only layers, and ID-mapped lower support; many probe results are cached under `runhome` as feature marker files. Layer creation builds the overlay layout: per-layer `diff`, `work`, `merged`, `empty`, `link`, and optional `lower` files, plus `home/l/<random>` symlinks pointing to `../<id>/diff`. `Get` resolves lower symlinks across primary/image/additional stores, optionally mounts composefs blobs, applies ID-mapped bind mounts, assembles mount data, falls back to relative `mountOverlayFrom` when mount data exceeds a page, and increments a ref counter. `Put` decrements the counter, unmounts via FUSE helpers or `unix.Unmount`, cleans leaked mapped mounts, and atomically refreshes `merged`.

## State And Persistence
Persistent state lives in the driver home: layer directories, the `l` symlink farm, per-layer `lower` and `link` files, `additionallayer` pointer files, optional `composefs-data`, staging directories, temp deletion roots, and XFS project-quota metadata. Runtime state lives in `runhome`, including feature cache files and private mountpoints for additional stores. The driver can repair missing `l` symlinks or `link` files via `recreateSymlinks`; staging locks are tracked in memory and on disk with `staging.lock`.

## Dependencies And Integration Points
The file integrates with the graphdriver registry, `graphdriver.RefCounter`, quota package, internal dedup, staging lockfiles, tempdir deletion, idtools/idmap, mount helpers, SELinux labels, archive/chrootarchive, overlay feature checks from sibling files, composefs helpers, and additional image/layer store contracts. It exposes additional image stores to higher storage layers and wraps itself with naive diff and naive ID-map update helpers when native overlay semantics are unsuitable.

## Risks And Edge Cases
Mount data length, lower depth (`maxDepth`), stale symlink farms, missing feature-cache consistency, rootless/network filesystem constraints, metacopy compatibility, FUSE force-mask behavior, additional-store lock expectations, and ID-mapped mount cleanup are high-risk areas. `useNaiveDiff` is guarded by package-level `sync.Once`, so global native-diff choice is process-wide. `getMergedDir` explicitly documents a locking risk around `DiffSize`. Composefs data-only lower separator support and extra composefs mounts add failure paths that must be unwound carefully.

## Test Signals
`overlay_test.go` exercises general graphdriver create/snapshot/diff/list behavior, deep lower reads, force-mask xattr preservation, shifting support differences for native versus mount-program overlay, and benchmarks. The broader codebase likely covers feature probes and additional store behavior indirectly, but the most complex mount assembly and composefs paths need environment-specific integration tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/drivers/overlay/overlay.go -->
