<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/converter_fuzz_test.go -->
# sources/cloud-native/containerd/core/remotes/docker/converter_fuzz_test.go

Purpose: fuzz target for `ConvertManifest`.

Important APIs/types/functions: `FuzzConvertManifest` generates arbitrary OCI descriptors and invokes `ConvertManifest` against a temp local content store.

Control flow: fuzz input populates an `ocispec.Descriptor`; a local content store is created; conversion is called and errors are ignored. Logging is set to panic level to suppress expected warnings for non-manifest media types.

State and persistence: uses a temporary local content store.

Dependencies and integration points: protects manifest conversion against malformed descriptor inputs and content-store edge cases.

Risks covered: panic resistance only; most fuzz descriptors will not reference valid content, so semantic conversion success is sparse.

Test signals: complements any deterministic converter tests elsewhere by widening malformed-input coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/converter_fuzz_test.go -->
