<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/imagestore.pb.go -->
# sources/cloud-native/containerd/api/types/transfer/imagestore.pb.go

Purpose: generated bindings for image-store transfer configuration, covering image naming, platform filtering, metadata walking, and unpack instructions.

Important APIs/types/functions: `ImageStore` has name, labels, platforms, all-metadata flag, manifest limit, extra references, and unpack configurations. `UnpackConfiguration` carries platform and snapshotter. `ImageReference` describes import/lookup naming behavior with prefix, overwrite, add-digest, and skip-named-digest flags.

Control flow: generated descriptor/map setup and getters only.

State/persistence: request/response metadata for transfer operations. Labels can be applied to stored images; platform and manifest options control content graph traversal; unpack config triggers snapshotter state changes in consumers.

Dependencies/integration: imports `types/platform.proto` and generated platform types. Transfer service and proxy code use these messages when importing/exporting/pulling/pushing image content.

Risks: naming flags interact subtly and can overwrite or suppress references. `ManifestLimit` can trade completeness for bounded traversal. Multiple unpack configs can cause partial success/failure complexity.

Test signals: transfer tests should cover prefix matching, digest reference creation, overwrite policy, all metadata versus platform-limited transfer, manifest limits, and multi-platform unpack.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/imagestore.pb.go -->
