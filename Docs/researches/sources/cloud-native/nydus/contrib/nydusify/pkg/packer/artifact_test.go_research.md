# sources/cloud-native/nydus/contrib/nydusify/pkg/packer/artifact_test.go

Purpose: verifies artifact path derivation and output directory creation.

Important APIs under test: `NewArtifact`, `bootstrapPath`, `blobFilePath`, `outputJSONPath`, and `ensureOutputDir`.

Control flow and state: tests cover default and explicit output directories, extension-preserving metadata paths, extension-to-blob rewriting, digest-named blob paths, `.` output JSON path behavior, and nested directory creation.

Dependencies and integration points: local filesystem and testify require.

Risks and test signals: confirms default `.nydus-build-output` creation and cleanup in one test. Does not cover permission errors or unusual path separators.
