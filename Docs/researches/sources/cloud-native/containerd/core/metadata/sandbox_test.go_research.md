# sources/cloud-native/containerd/core/metadata/sandbox_test.go

Purpose: validates sandbox store persistence, update semantics, filtering, duplicate handling, and delete behavior.

Important APIs and helpers: tests call `NewSandboxStore`, `Create`, `Get`, `Update`, `List`, and `Delete`. `assertEqualInstances` uses `cmp.Diff` with shared comparison options such as `compareAny` and `ignoreTime`.

Control flow: tests create sandboxes with labels, protobuf `Any` specs/options, typeurl extensions, runtime data, and sandboxer strings. Update tests mutate one label, add one extension, and replace spec via fieldpaths. List tests check full listing and `id==1` filtering. Delete removes a sandbox then expects a subsequent get to return not found.

State and persistence: exercises nested runtime option storage, extension maps, sandboxer persistence, and timestamp-insensitive equality. It checks compatibility with nil and populated `Any` fields.

Dependencies and integration: uses `core/sandbox`, protobuf types, `typeurl`, errdefs, go-cmp, and metadata test DB helpers.

Risks: timestamps are ignored in equality, so only presence through production validation is indirectly covered. Runtime immutability on no-fieldpath update is not directly tested here.

Test signals: good CRUD and fieldpath coverage for `sandbox.go`; limited coverage for invalid IDs beyond missing get and for invalid fieldpaths.
