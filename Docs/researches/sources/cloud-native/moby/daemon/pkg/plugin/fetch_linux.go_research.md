<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/fetch_linux.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/fetch_linux.go

## Purpose
Implements Linux plugin image fetch, metadata capture, layer extraction, and progress reporting.

## Important APIs, Types, And Functions
Key pieces are `setupProgressOutput`, `Manager.fetch`, `applyLayer`, `childrenHandler`, `fetchMeta`, `storeFetchMetadata`, `validateFetchedMetadata`, and `withFetchProgress`.

## Control Flow
Fetch normalizes the reference, sets plugin-specific auth scope and media-type prefix, resolves and fetches content through containerd handlers, and falls back to older Accept headers when resolution fails. Handlers record config/manifest/layer digests, skip plugin config children, apply layers to rootfs, and stream layer status from the content store.

## State, Dependencies, And Integration Points
Writes fetched blobs to `pm.blobStore` and extracts rootfs files into caller-provided directories. It depends on containerd remotes/content/images, Moby progress utilities, chrootarchive, registry auth, and OCI descriptors.

## Risks And Test Signals
A TODO notes multi-layer extraction order risk. Progress goroutines use context cancellation carefully but are timing-sensitive. Backend pull/upgrade/create flows are integration signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/fetch_linux.go -->
