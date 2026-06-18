## sources/cloud-native/moby/daemon/internal/image/image.go

Purpose: Defines the daemon image configuration model, image IDs, V1 compatibility fields, rootfs/history relationship, JSON behavior, and exporter interface.

Important APIs/types: `ID` wraps `digest.Digest`; `V1Image` contains legacy Docker image fields; `Image` embeds `V1Image` and adds content-addressable parent ID, `RootFS`, `History`, OS details, cached raw JSON, computed ID, and optional containerd `Details`. Methods expose raw JSON, ID, run config, base arch/variant/OS, platform, and custom marshal behavior. `ChildConfig`, `NewImage`, `NewChildImage`, `Clone`, `History`, `NewHistory`, `Exporter`, and `NewFromJSON` are the core helpers.

Control flow: `NewFromJSON` unmarshals config, requires a `RootFS`, stores immutable raw JSON, and leaves `computedID` to callers. `MarshalJSON` marshals through an alias then re-marshals a `map[string]*RawMessage` to stabilize top-level key order. `NewChildImage` clones or creates rootfs, appends non-empty layers, creates a history entry from the container command, and copies selected platform fields. `Clone` shallow-copies an image, clones rootfs, updates legacy ID and computed ID.

State and persistence: Image config is persisted as JSON by image stores and tar exporters. `rawJSON` preserves original bytes for content-addressable IDs and export.

Dependencies and integration: Integrates container config types, daemon layer DiffID, OCI platform/history descriptors, and digest IDs.

Risks: `Clone` assumes `RootFS` is non-nil. `Platform` returns raw Architecture/OS fields, while `OperatingSystem` and `BaseImgArch` default missing values to runtime; callers must choose the right one. Key-order stabilization depends on JSON map marshal ordering.

Test signals: `image_test.go` covers JSON parsing, missing RootFS, key order, ID helpers, OS defaulting, and child image rootfs copy behavior.
