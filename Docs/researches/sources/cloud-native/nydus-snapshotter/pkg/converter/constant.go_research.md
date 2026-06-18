# sources/cloud-native/nydus-snapshotter/pkg/converter/constant.go

Purpose: centralizes media types and annotations used to identify nydus manifests, blobs, bootstrap layers, cache manifests, and source/target relationships.

Important APIs and constants: manifest constants include `ManifestOSFeatureNydus`, `ManifestConfigNydus`, `ManifestArtifactTypeNydus`, `MediaTypeNydusBlob`, and `BootstrapFileNameInLayer`. Layer annotations include fs version, blob marker, blob digest/size, bootstrap marker, source chain/digest, target digest, encrypted blob marker, reference blob IDs, and uncompressed diff ID label.

Control flow: no executable logic.

State and persistence: constants define OCI descriptor annotations and media types persisted into content store manifests/layers and consumed by runtime/conversion logic.

Dependencies and integration points: used by `convert_unix.go`, `reconvert_unix.go`, cache/runtime code outside this subset, and tests that detect nydus blobs/bootstrap layers.

Risks: these string constants are cross-component contracts; changing them would break existing images and runtime detection. Some constants are not used in this subset but may be part of external compatibility.

Test signals: detection helpers and reconvert tests indirectly validate key blob/bootstrap/uncompressed annotation names.
