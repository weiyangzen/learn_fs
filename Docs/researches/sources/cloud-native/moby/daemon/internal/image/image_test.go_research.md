## sources/cloud-native/moby/daemon/internal/image/image_test.go

Purpose: Tests core image model helpers.

Important tests: `TestNewFromJSON` checks raw JSON preservation. `TestNewFromJSONWithInvalidJSON` requires the RootFS key. `TestMarshalKeyOrder` confirms stable top-level key order for selected fields. `TestImage` verifies ID string helpers, runtime OS defaulting, and run config access. `TestImageOSNotEmpty` verifies explicit OS wins. `TestNewChildImageFromImageWithRootFS` checks diff ID append, author/comment/config propagation, OS assignment, history append, and parent rootfs copy rather than mutation.

Control flow and state: Uses static sample JSON and a parent rootfs/history fixture.

Dependencies and integration: Uses container configs, daemon layer DiffID, runtime GOOS, and `go-cmp`/`gotest.tools`.

Risks covered: Missing RootFS rejection, raw JSON content, key order, and child image mutation boundaries. Gaps include empty-layer child behavior, nil RootFS clone behavior, and platform OS feature/version propagation details.

Persistence: Validates the JSON representation consumed by image stores and exporters.
