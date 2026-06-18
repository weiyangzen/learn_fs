<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ocf_cache.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ocf_cache.cpp

## Purpose
Builds a Photon `IFileSystem` adapter that caches reads through Open CAS Framework while preserving source-file EOF semantics.

## Important APIs, Types, And Functions
Defines `OcfTruncateFile`, `OcfCachedFile`, `OcfCachedFs`, and public factory `FileSystem::new_ocf_cached_fs`.

## Control Flow
Factory creates and initializes an `OcfNamespace`, then constructs `OcfCachedFs`. `OcfCachedFs::init` validates prefetch alignment, sets global OCF allocator, derives media size, creates `ease_ocf_provider`, and starts or reloads the cache. `open` resolves source file namespace metadata through an object pool and returns an `OcfTruncateFile` wrapping an `OcfCachedFile`. Reads go `OcfTruncateFile` EOF clamp -> `OcfCachedFile::pread` -> `OcfCachedFs::ocf_pread` -> provider.

## State And Persistence
Persists cached blocks in `media_file` and file namespace mappings in the namespace filesystem. Keeps pooled `OcfSrcFileCtx` objects keyed by path. Destructor stops provider and frees namespace/params/provider ownership.

## Dependencies And Integration Points
Depends on Photon filesystem adapters, `ObjectCache`, `IOAlloc`, OCF namespace, and ease OCF bindings. Exposes the cache through `cache.h` factory conventions.

## Risks And Test Signals
Only open/read/fadvise/fstat/vioctl paths are implemented; most filesystem mutations return unimplemented. `OcfCachedFile` destructor releases by pathname, so pooling correctness depends on path consistency. `fadvise(POSIX_FADV_WILLNEED)` performs a real read into allocated memory. Source size reviewed: 295 lines; performance/manual coverage is `ocf_perf_test`.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ocf_cache.cpp -->
