<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/compat/compat.go -->
## sources/cloud-native/buildkit/solver/llbsolver/compat/compat.go

Purpose: defines supported BuildKit LLB compatibility versions and validation logic.

Important APIs and types: constants `CompatibilityVersion013`, `CompatibilityVersion015`, `CompatibilityVersion031`, `CompatibilityVersionCurrent`, `JobValueKey`, `SupportedCompatibilityVersions`, and `ValidateCompatibilityVersion`.

Control flow: supported versions are stored in a slice and returned as a clone to prevent caller mutation. Validation accepts known versions, reports a special "upgrade buildkit" error for versions newer than current, and reports supported values for older unsupported versions.

State and dependencies: static in-memory constants only. Dependency on `slices` and `pkg/errors`.

Integration points: solver jobs store compatibility with `Job.SetValue` under `JobValueKey`; exporter code reads `Job.CompatibilityVersion` and passes it to exporters.

Risks and test signals: forgetting to update `CompatibilityVersionCurrent` or tests when adding a version would reject newer clients. `compat_test.go` covers current list, valid versions, unsupported old-ish version, and future-version message.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/compat/compat.go -->
