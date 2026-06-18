# sources/cloud-native/nydus/contrib/nydusify/pkg/converter/converter_test.go

Purpose: tests standard conversion input validation and model conversion helper flows using monkey patching.

Important APIs and flow: `TestConvert` covers model dispatch errors, invalid platform, and invalid push retry delay. `TestConvertModelFile` and `TestConvertModelArtifact` patch modctl/external/pack/push helpers to verify success and each failure stage. `TestPackWithAttributes`, `TestPackFinalBootstrap`, `TestBuildNydusImage`, `TestMakeDesc`, `TestBuildModelConfig`, `TestPushManifest`, and `TestGetSourceManifestSubject` exercise helper behavior, remote fallback, gzip/bootstrap handling, and descriptor creation with mocks.

State and persistence: uses `/tmp/nydusify` and temp files, with cleanup in tests; monkey patches external functions and remote pushes.

Dependencies and integration: provides regression signal for orchestration and error wrapping across modctl, snapshotter-converter, remote provider, parser image descriptors, and model-spec.

Risks and test signals: broad but heavily mocked, so it validates call sequencing more than real conversion correctness. Some tests use fixed `/tmp/nydusify`, which can be sensitive to parallel runs or leftover files.
