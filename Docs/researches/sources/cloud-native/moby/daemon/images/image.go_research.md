<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image.go -->
# sources/cloud-native/moby/daemon/images/image.go

Purpose: implements image lookup and platform compatibility checks for the legacy image service.

Important APIs and control flow: `ErrImageDoesNotExist` is a NotFound-style error. `manifestMatchesPlatform` looks at content leases named for an image, reads manifest lists and manifests from the content store, and checks whether a requested platform points to the image config digest. `GetImage` parses references, resolves named references through the refstore, falls back to image ID search, and on return verifies requested platforms with `OnlyPlatformWithFallback` plus the manifest-list fallback. `OnlyPlatformWithFallback` wraps `platforms.Only` and accepts images whose config lacks a CPU variant when OS and architecture match.

State and persistence: reads image store records, reference store entries, content store blobs, and content lease resources. It does not mutate state.

Dependencies and integration: used by almost every image API. It integrates distribution references, containerd content/lease APIs, OCI platform matching, and daemon API error classification.

Risks: `GetImage` can return both a non-nil image and a NotFound error on platform mismatch, and callers must handle that special case. `manifestMatchesPlatform` reads only up to 1 MB of content and skips malformed or missing resources with logs, so corrupt lease content may degrade platform validation rather than fail hard. The legacy store cannot model multiple platform variants for one tag cleanly.

Test signals: `images_test.go` covers the CPU-variant fallback matcher. Platform mismatch behavior is covered indirectly by pull/build paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/image.go -->
