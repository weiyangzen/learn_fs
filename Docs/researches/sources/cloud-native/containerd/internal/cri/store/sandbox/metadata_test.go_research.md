# Research: sources/cloud-native/containerd/internal/cri/store/sandbox/metadata_test.go

This test file validates sandbox metadata JSON serialization. `TestMetadataMarshalUnmarshal` constructs a `Metadata` value with ID, name, and CRI pod sandbox metadata. It confirms normal `json.Marshal` matches an explicit `versionedMetadata` wrapper, direct `MarshalJSON` can be decoded by `UnmarshalJSON`, the wrapper can be decoded through `json.Unmarshal`, and `json.Marshal` output can be passed back to `UnmarshalJSON`.

The unsupported-version case builds a wrapper with a random version and asserts unmarshalling into `Metadata` fails. This protects the versioning contract used when sandbox metadata is checkpointed in containerd labels.

The test signal is focused on payload format compatibility, not full field coverage. It does not populate netns path, IPs, runtime handler, CNI result, process label, or nil config edge cases. There is no filesystem persistence or containerd label integration in the test. It guards the core risk that recursive JSON methods or unsupported-version handling could break recovery of sandbox metadata.
