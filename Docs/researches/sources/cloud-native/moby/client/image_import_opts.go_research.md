<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_import_opts.go -->
# sources/cloud-native/moby/client/image_import_opts.go

Purpose: declares option structures for image import.

Important APIs/types: `ImageImportSource{Source io.Reader, SourceName string}` and `ImageImportOptions{Tag, Message string, Changes []string, Platform ocispec.Platform}`.

Control flow and dependencies: no runtime flow. Depends on `io` and OCI platform types.

State and integration behavior: no persistence. These types define how callers provide either a source stream or source name plus metadata consumed by `ImageImport`.

Risks and test signals: risks are ambiguous combinations of `Source` and `SourceName` and platform formatting limitations. The production method and package tests enforce behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_import_opts.go -->
