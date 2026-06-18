# sources/cloud-native/moby/integration/internal/image/load.go

Purpose: helper for loading generated OCI image layouts into a daemon during integration tests.

Important APIs and helpers: `Load(ctx, t, apiClient, imageFunc)` where `imageFunc` is a `specialimage.SpecialImageFunc`.

Control flow: creates a temp directory, calls the special image builder to write an OCI layout and return an index, archives the directory, calls `ImageLoad` with quiet output, drains and closes the response, and returns the digest string of the first manifest in the returned index.

State and persistence: writes temporary OCI layout files and imports them into the daemon image store. The returned digest identifies the loaded image content.

Dependencies and integration: depends on specialimage builders, archive/tar helper, image load API, OCI index descriptors, and testing assertions.

Risks: assumes the generated index has at least one manifest. It drains load output but does not parse load messages, so it trusts API success.

Test signals: helper-only; enables many image integration tests to construct precise content, platform, layer, label, and attestation scenarios.
