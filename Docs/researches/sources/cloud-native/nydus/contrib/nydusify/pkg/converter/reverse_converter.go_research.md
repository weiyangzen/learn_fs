# sources/cloud-native/nydus/contrib/nydusify/pkg/converter/reverse_converter.go

Purpose: provides experimental reverse conversion from a Nydus image back to a conventional OCI image.

Important APIs/functions: `ReverseConvert` is the main entry point. `reconvertWithSnapshotter` wires containerd nydus-snapshotter conversion functions with the local provider content store.

Control flow: `ReverseConvert` enters the `nydusify` containerd namespace, parses requested platforms, prepares a work directory and temporary subdirectory, constructs a converter provider, parses push retry delay, optionally enables plain HTTP, pulls the source image, resolves its root descriptor, reconverts it through snapshotter converter functions, and pushes the returned OCI descriptor to the target reference.

State and persistence: work directories are temporary unless the configured work dir pre-exists. The provider content store holds pulled source descriptors and generated converted descriptors. Push retry count/delay and plain HTTP state live on the provider.

Dependencies and integration points: containerd namespaces/platforms, Harbor platform parsing, converter provider, nydus-snapshotter `LayerReconvertFunc`, `UnpackOption`, and `DefaultIndexConvertFunc`, plus `nydus-image` path and compressor options.

Risks and test signals: marked experimental. Failure points include duration parsing, work-dir permissions, registry pull/push, missing source descriptors, nil converter result, and external builder behavior. It relies on snapshotter reconversion semantics for manifest/index correctness.
