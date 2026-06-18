# sources/cloud-native/nydus-snapshotter/config/daemonconfig/daemonconfig_test.go

Purpose: tests for FUSE daemon config JSON behavior and secret filtering.

Flow: unmarshals representative registry/backend/cache config, verifies embedded fs prefetch fields and backend fields, checks `amplify_io` pointer preserves non-zero and zero while omitting nil, and serializes a filtered config to ensure secret auth disappears while other fields survive.

State/dependencies: in-memory JSON only; uses testify require.

Integration points: protects nydusd config compatibility and backend-source safe serialization.

Risks/signals: tests do not exercise atomic file writes, mirror selection, auth fill, or supplementation paths.
