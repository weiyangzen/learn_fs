# sources/cloud-native/nydus/contrib/nydusify/pkg/cache/cache.go

## Purpose
This package implements Nydus build cache manifests. It maps source layer chain IDs to generated Nydus bootstrap/blob descriptors so later conversions can skip rebuilding layers and reuse cached artifacts.

## Important APIs, Types, and Functions
`Opt` configures max records, cache version, RAFS fs version, Docker media type compatibility, and backend. `Cache` holds remote, pulled records, reference records, and records to push. Key methods are `New`, `GetReference`, `SetReference`, `recordToLayer`, `exportRecordsToLayers`, `layerToRecord`, `importRecordsFromLayers`, `Export`, `Import`, `Check`, `Record`, `PullBootstrap`, and `Push`. `Record.GetReferenceBlobs` parses referenced blob IDs.

## Control Flow
Import resolves and pulls a cache manifest, validates cache version and fs version, and imports layers into records. `layerToRecord` parses bootstrap, blob, or reference blob layers from annotations. `recordToLayer` emits bootstrap and optional blob descriptors, with different behavior for registry versus object backends. `Record` maintains a bounded front-biased queue. `Export` emits layers, builds config rootfs diff IDs, pushes config, then pushes the cache manifest. `Check` verifies cached bootstrap and blob availability and returns readers.

## State, Persistence, and Dependencies
Persistent state is the remote cache image manifest/config/layers and possibly backend blob objects. In-memory state is maps by digest and ordered pushed records. Dependencies include containerd image media types, OCI descriptors, digest, local backend/remote/utils packages, and JSON.

## Integration Points
Converter code uses this package for `--build-cache` and related flags. It integrates tightly with backend type behavior: registry stores blob layers in the cache manifest, while OSS/S3 record blob digest/size annotations on bootstrap layers.

## Risks and Test Signals
Risk includes nil backend assumptions in `recordToLayer`, invalid or missing annotations silently dropping records, optimistic registry checks, and diff ID compatibility with Docker pulls. `exportRecordsToLayers` assumes referenced registry records exist before dereferencing blob descriptors. Tests are broad for record/layer conversion, queue behavior, import/export success and errors, check paths, and pull/push wrappers, but most remote behavior is mocked.
