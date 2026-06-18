<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/cache.h -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/cache.h

Purpose: Public cache interfaces and factory declarations.

APIs and types: Defines cache open flags, read/write v2 flags, stat marker helpers, `IOCTL_GET_PAGE_SIZE`, `ICachedFileSystem`, `ICachedFile`, and factories for generic, full-file, OCF, and download caches. `ICachedFile` maps refill to writes, prefetch to `fadvise(WILLNEED)`, query to `fiemap`, and eviction to `trim`.

State and persistence: Interface abstracts persistent cache stores and source filesystems.

Dependencies and integration: Consumed by `ImageService`, cache implementations, and wrappers.

Risks and test signals: Some methods are `UNIMPLEMENTED` in interfaces and only valid through concrete types. Build and cache-mode smoke tests verify factory linkage.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/cache.h -->
