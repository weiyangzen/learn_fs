<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/imagestore.proto -->
# sources/cloud-native/containerd/api/types/transfer/imagestore.proto

Purpose: source schema for image-store endpoints in transfer workflows.

Important APIs/types/functions: `ImageStore` identifies an image name and labels, platform filters, all-metadata/manifest-limit traversal settings, extra import references, and repeated `UnpackConfiguration`. `UnpackConfiguration` selects platform and snapshotter. `ImageReference` encodes prefix/digest/overwrite matching and storing rules.

Control flow: schema comments define resolver/store behavior; actual traversal/unpack logic is in transfer implementations.

State/persistence: influences image metadata records, content graph retention, and snapshotter unpack state created by transfer operations.

Dependencies/integration: imports `types/platform.proto`; consumed by transfer API and client `TransferService`.

Risks: spelling/comment typo in snapshotter comment aside, the main risk is ambiguous reference policy. Incomplete platform selections or low manifest limits can omit content users expect.

Test signals: generated code, transfer image import/export cases, naming conflict handling, and unpack per platform/snapshotter.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/transfer/imagestore.proto -->
