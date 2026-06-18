<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/display/manifest_printer.go -->
# sources/cloud-native/containerd/pkg/display/manifest_printer.go

Purpose: render OCI image, manifest, index, config, layer, and content metadata as a readable tree.

Important APIs and types: `TreeFormat`, `LineTreeFormat`, `ImageTreePrinter`, options `Verbose`, `WithWriter`, `WithFormat`, constructor `NewImageTreePrinter`, and methods `PrintImageTree`, `PrintManifestTree`, `printManifestTree`, and `showContent`.

Control flow and state: the printer writes to its configured writer, recursively reads descriptors from a content store, prints descriptor media type/digest/size/platform, unmarshals manifests or indexes, and prints child config/layer/manifest entries with tree prefixes. Verbose mode prints content labels and indented JSON content for JSON media types.

Dependencies and integration: integrates containerd `content` and `images`, OCI image spec descriptors, platform formatting, and `errdefs.IsNotFound` handling.

Risks and test signals: tree output order follows manifest/index order but map label order is not deterministic. Missing local content is non-fatal and displayed as skipped, while other content errors abort printing.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/display/manifest_printer.go -->
