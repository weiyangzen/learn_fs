# sources/cloud-native/containers-storage/types/options_test.go

Purpose: unit tests for rootless storage option derivation and config decode warning behavior.

Important APIs and control flow: `TestGetRootlessStorageOpts` preserves and clears `STORAGE_DRIVER`, then exercises unset, valid, overlay2, unsupported, and environment-specified drivers. It expects invalid system drivers to be replaced by overlay or vfs unless overridden by `STORAGE_DRIVER`. `TestGetRootlessStorageOpts2` verifies `$HOME` and `$UID` expansion in `RootlessStoragePath`. `TestReloadConfigurationFile` captures logrus output while loading `storage_broken.conf`, then asserts both a valid runroot and the undecoded-key warning.

State and persistence: uses temporary directories and environment mutation via `t.Setenv` or manual restore. It relies on package globals in `options.go`, so test ordering and environment cleanup matter.

Dependencies and integration: uses `gotest.tools/v3/assert`, `stretchr/testify/require`, logrus, and rootless UID helpers. Test fixtures are local TOML files.

Risks: rootless overlay capability makes expected driver host-dependent. Manual environment restoration in the first test predates `t.Setenv` and must remain correct if subtests become parallel.

Test signals: coverage confirms driver normalization, environment override precedence, path expansion, and malformed config warning emission.
