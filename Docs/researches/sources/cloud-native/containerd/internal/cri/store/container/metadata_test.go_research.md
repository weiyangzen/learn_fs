# Research: sources/cloud-native/containerd/internal/cri/store/container/metadata_test.go

This test file verifies container metadata JSON round-tripping. `TestMetadataMarshalUnmarshal` constructs a `Metadata` value with ID, name, sandbox ID, CRI container metadata, image reference, and log path. It compares normal `json.Marshal` output with the explicit `versionedMetadata` wrapper, checks direct `MarshalJSON` followed by `UnmarshalJSON`, direct `MarshalJSON` followed by `json.Unmarshal` into the wrapper type, and `json.Marshal` followed by `UnmarshalJSON`.

The unsupported-version case constructs a wrapper with a random version and asserts unmarshalling into `Metadata` fails. This protects the version gate in `UnmarshalJSON` and the non-recursive wrapper format.

The test signal focuses on serialization compatibility for metadata checkpointing in containerd labels. It does not test every metadata field, notably stop signal and process label, nor nil config behavior or migration from older versions. There is no filesystem persistence in this test; it validates only the JSON payload shape that other persistence layers store.
