# sources/cloud-native/nydus/contrib/nydusify/pkg/parser/parser.go

Purpose: parses OCI/Nydus image references into manifest, config, index, and categorized OCI/Nydus image objects.

Important APIs/types/functions: `Parser`, `Image`, `Parsed`, `New`, `FindNydusBootstrapDesc`, pull helpers, `parseImage`, `PullNydusBootstrap`, `matchImagePlatform`, and `Parse`.

Control flow: `Parse` resolves the remote descriptor, then handles single manifests or indexes. Single manifests are pulled once and classified as Nydus when the last layer is a gzip layer annotated as Nydus bootstrap. Indexes are searched for matching linux arch; descriptors are classified via artifact type, platform features, or manifest inspection. `parseImage` pulls config and enforces OS/arch unless ignoreArch is enabled for single manifests.

State and persistence: parser stores the remote and interested arch. It does not cache fetched JSON beyond returned parsed structs.

Dependencies and integration points: remote registry wrapper, containerd media types, OCI specs, nydus utility annotations/platforms, and optimizer/provider flows needing parsed images.

Risks and test signals: index parsing can overwrite earlier matches with later descriptors. Images with no matching platform return parsed results with nil images instead of a direct error. Certificate errors only trigger a warning hint.
