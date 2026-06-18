# sources/control-plane/csi-lib-utils/protosanitizer/test/csitest.proto Research

## Purpose
`csitest.proto` is a modified CSI-like schema built specifically to test secret stripping in `protosanitizer`. The accompanying README says it is a modified version of the CSI 1.0.0 spec whose only purpose is to test stripping of secret fields. It keeps the familiar CSI `Identity`, `Controller`, and `Node` service shapes while adding deliberately awkward `csi.v1.csi_secret` placements that exercise descriptor-based redaction beyond the normal upstream `secrets` maps.

The schema lives in package `csitest.v1` and generates Go code under `github.com/kubernetes-csi/csi-lib-utils/protosanitizer/test/csitest`. It imports `csi.proto` specifically to use the `csi.v1.csi_secret` field option, so it validates that redaction is based on descriptor options rather than a hard-coded package, message name, or field name.

## Important APIs, Types, And Functions
The service set is a compact CSI 1.0 style surface:

- `Identity`: plugin info, capabilities, and probe.
- `Controller`: create/delete volume, publish/unpublish, validate capabilities, list volumes, get capacity, controller capability discovery, create/delete/list snapshots.
- `Node`: stage/unstage, publish/unpublish, get volume stats, get capabilities, and get info.

Most message types mirror CSI 1.0 structures: plugin info/capability messages, `CreateVolumeRequest`, `VolumeContentSource`, `CreateVolumeResponse`, `VolumeCapability`, `CapacityRange`, `Volume`, topology messages, controller publish/unpublish messages, validation messages, list messages, capacity messages, controller capability messages, snapshot messages, node stage/publish/stat messages, usage messages, node capability messages, and node info messages.

The test-specific secret API is concentrated in these fields:

- `CreateVolumeRequest.seecreets`: a renamed `map<string,string>` secret field, proving redaction is option-driven rather than name-driven.
- `CreateVolumeRequest.new_secret_int`: a scalar `int64` marked secret, proving secrets are not limited to string maps.
- `CreateVolumeRequest.maybe_secret_map`: an unmarked map whose values are `VolumeCapability`; this forces recursion into map values.
- `VolumeContentSource.VolumeSource.oneof_secret_field`: a secret nested inside a message selected through a oneof.
- `VolumeContentSource.nested_secret_field`: a secret in a nested message reachable from `CreateVolumeRequest.volume_content_source`.
- `VolumeCapability.array_secret`: a secret field inside messages that commonly appear in repeated arrays and map values.
- Standard `secrets` maps on delete, publish, unpublish, validate, snapshot, and node stage/publish requests.

## Control Flow
Like `csi.proto`, this file is declarative, but it is designed around a concrete sanitizer execution path. The generated `csitest.CreateVolumeRequest` in `protosanitizer_test.go` populates `Seecreets`, `NewSecretInt`, repeated `VolumeCapabilities` with `ArraySecret`, `MaybeSecretMap` values with `ArraySecret`, and `VolumeContentSource.Volume.OneofSecretField` plus `NestedSecretField`.

When passed to `StripSecrets`, the sanitizer should:

1. Visit only populated fields through protobuf reflection.
2. Replace `seecreets` and `new_secret_int` immediately because those fields carry `csi.v1.csi_secret`.
3. Recurse through the unmarked `maybe_secret_map`, stringify int64 map keys, and redact each nested `VolumeCapability.array_secret`.
4. Recurse through repeated `volume_capabilities` and redact each element's `array_secret` while preserving non-secret mount data.
5. Recurse through `volume_content_source`, follow the selected `volume` oneof, redact `oneof_secret_field`, preserve `volume_id`, and redact `nested_secret_field`.

The schema also supports a compatibility test where a `csitest.CreateVolumeRequest` is marshaled and unmarshaled into the current upstream `csi.CreateVolumeRequest`. That path verifies that fields unknown to the older type are not exposed in sanitizer output.

## State, Persistence, And Dependencies
The proto itself has no mutable state. Its durable output is the generated `test/csitest/csitest.pb.go`, including descriptor data, Go structs, oneof wrappers, map entry types, and service descriptors. The `test/Makefile` pins `protoc` default version `25.2`, installs `protoc-gen-go`, and runs `protoc --go_out=csitest --go_opt=paths=source_relative csitest.proto`.

The file depends on protobuf descriptor, timestamp, and wrapper imports plus local `csi.proto` for the `csi.v1.csi_secret` extension. The generated code is imported by `protosanitizer_test.go`, where populated messages become test inputs for the runtime sanitizer.

## Integration Points
`csitest.proto` is tightly integrated with `protosanitizer_test.go`. The expected JSON string in `TestStripSecrets` names the generated text names: `seecreets`, `new_secret_int`, `maybe_secret_map`, `array_secret`, `nested_secret_field`, and `oneof_secret_field`. Any schema change that alters those field names, field numbers, oneof structure, or secret options must update both generated Go and expected test output.

The file also integrates with the upstream-like `csi.proto` fixture. Because it imports `csi.proto` only for the extension, it is a focused guard against implementations that redact based on exact CSI request type or on a field literally named `secrets`. It proves that any field in any generated protobuf package carrying the CSI secret option is treated as sensitive.

## Risks
The most important risk is generated-code drift. `csitest.pb.go` must be regenerated after edits to this proto, or tests may run against stale descriptors. Because the sanitizer is descriptor-driven, stale generated descriptors can make source review misleading.

Another risk is accidental weakening of the fixture. Renaming `seecreets` back to `secrets`, removing scalar or nested secret fields, or marking `maybe_secret_map` itself as secret would reduce coverage of option-based, recursive redaction. Similarly, removing the oneof nesting would stop testing oneof traversal.

The import relationship with `csi.proto` is required. If the local extension definition diverges from the generated CSI package used by `protosanitizer.isCSI1Secret`, the test may fail or, worse, stop exercising the same extension identity as production.

As with the upstream-like schema, unmarked opaque fields remain visible. This is intentional for the fixture, but any future test additions should be explicit about whether a field is secret by option or merely sensitive by comment.

## Test Signals
Strong test signals are the exact expected JSON in `TestStripSecrets`: `seecreets`, `new_secret_int`, every `array_secret`, `nested_secret_field`, and `oneof_secret_field` must become `"***stripped***"`; `volume_id`, `name`, `capacity_range`, and mount `fs_type` must remain visible; integer map keys must become string JSON keys; and the original message must remain unchanged after formatting.

Build signals include successful `make build` in the `protosanitizer/test` directory, regenerated `csitest/csitest.pb.go` containing the test fields and oneof wrappers, and `go test` for the protosanitizer package. Regression tests should fail if redaction depends on the literal field name `secrets`, if scalar secret values leak, if recursion into maps/repeated messages/oneofs is removed, or if unknown future fields are logged after unmarshaling into an older CSI type.
