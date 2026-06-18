# sources/cloud-native/nydus-snapshotter/pkg/converter/tool/feature_test.go

Purpose: tests feature-set operations and builder help parsing for optional nydus-image features.

Important APIs and functions: `TestFeature` covers `Add`, `NewFeatures`, `Remove`, `Contains`, and `Equals`; `TestDetectFeature` checks help-text parsing for tar2rafs, batch-size, encrypt, unsupported old versions, and empty input; `TestDetectFeatures` checks process-wide detection behavior and env-disable handling.

Control flow: tests use hard-coded help text excerpts from multiple nydus-image versions. `TestDetectFeatures` resets package globals and `sync.Once` for isolated cases, then calls `DetectFeatures` with a fake `getHelp` function.

State and persistence: mutates package globals `requiredFeatures`, `detectedFeatures`, `detectFeaturesOnce`, and `disableTar2Rafs`, but only in-process.

Dependencies and integration points: validates logic that gates converter pack behavior without needing an actual `nydus-image` binary.

Risks and gaps: no direct test for `GetHelp` command execution or `buildPackArgs`. Because tests manually reset globals, production behavior with multiple builders/required sets remains intentionally constrained.

Test signals: strong coverage for supported/unsupported feature detection, env-disable semantics, set equality, and changed-required-feature error.
