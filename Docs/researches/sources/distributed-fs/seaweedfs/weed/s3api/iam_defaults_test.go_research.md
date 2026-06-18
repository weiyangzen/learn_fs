# Research: sources/distributed-fs/seaweedfs/weed/s3api/iam_defaults_test.go

## sources/distributed-fs/seaweedfs/weed/s3api/iam_defaults_test.go

Purpose: tests for advanced IAM configuration defaults, STS signing-key fallback, and default allow/deny behavior depending on whether an explicit IAM config file is supplied.

Important tests: `TestLoadIAMManagerFromConfig_Defaults`, `_Overrides`, `_PartialDefaults`, `_ExplicitEmptyKey`, and `_MissingKeyError` exercise STS duration/issuer/signing-key loading and fallback provider behavior. `TestLoadIAMManagerFromConfig_ExplicitFileDefaultsToDeny` verifies explicit config without `policy.defaultEffect` denies by default. `TestLoadIAMManagerFromConfig_NoFileDefaultsToAllow` preserves zero-config startup allow behavior. `TestLoadIAMManagerFromConfig_ExplicitFileEnforcesUserScopedPolicy` covers issue #8366 by loading roles/policies using `${jwt:preferred_username}` and checking arbitrary bucket creation is denied while the user bucket is allowed.

State and dependencies: tests create temporary JSON config files, call `loadIAMManagerFromConfig`, and query `manager.DefaultAllow` or `IsActionAllowed`. Dependencies include `iam/integration`, OS temp files, and testify. Integration points are S3 server startup flags, STS token signing, and policy engine variable substitution. Risks: a missing default signing key must fail clearly, while explicit config should not accidentally create an open S3 gateway. Test signal is broad for config loading and enforcement defaults.
