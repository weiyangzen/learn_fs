## sources/cloud-native/moby/daemon/internal/image/v1/imagev1.go

Purpose: Generates legacy V1 image IDs for backwards-compatible Docker archive save output.

Important APIs: `CreateID(v1Image, layerID, parent)` and helper `rawJSON`.

Control flow: `CreateID` clears the legacy image ID, marshals the V1 image, unmarshals into a map so it can inject `layer_id` and optional `parent`, marshals the map again, logs the generated JSON at debug level, and returns `digest.FromBytes(configJSON)`. `rawJSON` marshals a value and returns a `*json.RawMessage`, or nil on marshal failure.

State and persistence: The generated digest becomes legacy config identity in saved archives. No state is retained in memory.

Dependencies and integration: Called by tar export `saveImage` for every layer in an image. Depends on daemon image/layer types and OpenContainers digest.

Risks: Map marshal ordering and injected compatibility fields determine the digest; any JSON behavior change can alter legacy IDs. The FIXME notes slight incompatibility with RootFS logic.

Tests: No direct tests in this subset.
