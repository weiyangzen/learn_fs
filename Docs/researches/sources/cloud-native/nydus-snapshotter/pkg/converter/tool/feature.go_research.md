# sources/cloud-native/nydus-snapshotter/pkg/converter/tool/feature.go

Purpose: detects which optional `nydus-image create` features are supported by the installed builder and exposes a small feature-set type.

Important APIs and functions: `Feature` and `Features`; constants `FeatureTar2Rafs`, `FeatureBatchSize`, `FeatureEncrypt`, and env var `NYDUS_DISABLE_TAR2RAFS`; set methods `NewFeatures`, `Add`, `Remove`, `Contains`, `Equals`; `GetHelp`; `detectFeature`; `DetectFeatures`.

Control flow: `GetHelp` executes `builder create -h`. `detectFeature` checks exact feature text and, for two-part features like `--type tar-rafs`, accepts help text containing both parts. `DetectFeatures` runs only once process-wide via `sync.Once`, records the required feature set, scans help output, honors `NYDUS_DISABLE_TAR2RAFS`, warns for unsupported features, and returns the detected subset. Later calls with a different required set return an error.

State and persistence: process-global `requiredFeatures`, `detectedFeatures`, `detectFeaturesOnce`, and `disableTar2Rafs`. No disk state.

Dependencies and integration points: called by converter `Pack` before choosing streaming vs directory conversion and optional batch/encryption flags.

Risks: process-wide `sync.Once` means a first call with one builder path/feature set fixes detection for the entire process; using different builders later is unsupported. `disableTar2Rafs` is read at package init and only changed in tests. The two-part detection can produce false positives if help text mentions flag and value separately in unrelated contexts.

Test signals: `feature_test.go` covers set operations, detection across multiple representative help texts, env-based tar2rafs disable, and error on changed required feature sets.
