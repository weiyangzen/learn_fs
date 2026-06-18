<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/cache.go -->
# sources/cloud-native/moby/daemon/images/cache.go

Purpose: adapts `ImageService` to the legacy builder image-cache interface.

Important APIs and control flow: `cacheAdaptor` forwards image lookup, reference lookup, parent management, built-locally checks, and image creation to the service's image store. `Children` has special `FROM scratch` behavior: for an empty parent ID, it returns root images that were built locally. `Create` marshals an image config, creates the image, and optionally sets its parent. `MakeImageCache` constructs the actual cache with `cache.New`.

State and persistence: reads and writes image store records, parent links, and built-locally metadata. No layer data is written here.

Dependencies and integration: bridges `daemon/internal/image/cache`, the legacy builder package, the internal image store, and `ImageService.GetImage`.

Risks: `Children` logs and skips images when built-locally metadata cannot be read, which may reduce cache hits silently. `Create` ignores the diffID argument, so it relies on the supplied image config to be consistent with layers.

Test signals: no direct tests in this file; build cache behavior is covered indirectly by builder tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/cache.go -->
