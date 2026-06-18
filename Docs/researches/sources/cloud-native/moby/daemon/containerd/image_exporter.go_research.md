# sources/cloud-native/moby/daemon/containerd/image_exporter.go

## Purpose
Implements image save/load for the containerd image store, including multi-platform selection, Docker archive compatibility, content leases, referrer import/export, unpacking, and platform verification.

## Important APIs, Types, And Functions
- `ExportImage` saves named images, repositories, or explicit digests to a tar stream.
- `leaseContent` leases all reachable content descriptors while exporting.
- `LoadImage` imports a tar stream, handles requested platforms, creates dangling refs for unnamed/invalid images, warms identity cache, unpacks selected platforms, and logs load events.
- `verifyImagesProvidePlatform` checks imported images contain requested platform content.
- `referrersForImport`/`referrersForExport` expose OCI referrers from local content labels.

## Control Flow
Export builds archive options with platform filtering, skip-missing, non-distributable skip, and referrers. Repository names without tags export every tag in the repository; explicit digests are exported without a tag. Single-platform exports replace the target with the selected manifest descriptor. Load decompresses input, imports through containerd with platform/referrer options, optionally verifies requested platforms, unpacks host or requested platform manifests, emits progress lines, warms identity cache for named images, and logs events.

## State And Persistence
Export is read-only except for temporary leases. Load writes image records, dangling digest refs, content blobs, referrer labels, snapshots from unpack, identity cache warmup entries, progress output, and events.

## Dependencies And Integration Points
Depends on containerd archive import/export, content leases, compression, platform matchers, reference parsing, image resolution, push descriptor selection, referrer helpers, events, and identity cache warmup. It backs `docker save` and `docker load`.

## Risks And Edge Cases
Platform filtering is nuanced: no requested platforms tolerates missing variants, but explicit platforms turn missing content into not-found errors. Exporting by repository can include many tags. Import can succeed but unpack fail; errors are printed but the image remains imported. Referrer discovery parses labels and manifests best-effort, skipping malformed data.

## Test Signals
No direct tests in this subset. Save/load tests elsewhere should cover repository expansion, explicit digest exports, platform filtering, missing content, referrers, unpack warnings, and identity cache warmup.
