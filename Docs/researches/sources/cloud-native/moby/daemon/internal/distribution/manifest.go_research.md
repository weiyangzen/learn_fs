# sources/cloud-native/moby/daemon/internal/distribution/manifest.go

## Purpose
Caches registry manifests in a containerd content store and validates/detects manifest media types for pull-by-digest and local reuse.

## APIs, Control Flow, and Integration
`ContentStore` narrows containerd ingest/provider/update APIs. `manifestStore.Get` detects missing descriptor media type, opens a writer to retain/write content, returns cached local manifests when possible, otherwise fetches remote and persists via `Put`. `getLocal` verifies distribution-source labels for canonical refs, optionally checks remote existence, updates source labels, reads content, and unmarshals the manifest. Helpers manage sorted deduplicated `containerd.io/distribution.source.<domain>` labels. `detectManifestBlobMediaType` infers or validates Docker/OCI schema2/list/index/schema1 shapes.

## State, Dependencies, and Risks
State persists in containerd content blobs, active ingests, and content labels. Risks include serving cached digest content only after source verification, best-effort label update failures, ingest abort complexity, and strict media-type structural validation. Tests cover cache/no-cache, unknown media type, persistence failures, and detection invalid cases.
