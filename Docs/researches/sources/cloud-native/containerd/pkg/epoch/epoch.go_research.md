<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/epoch/epoch.go -->
# sources/cloud-native/containerd/pkg/epoch/epoch.go

Purpose: parse and manage the `SOURCE_DATE_EPOCH` environment variable for reproducible builds/artifacts.

Important APIs and constants: `SourceDateEpochEnv`, `SourceDateEpoch`, `ParseSourceDateEpoch`, `SetSourceDateEpoch`, and `UnsetSourceDateEpoch`.

Control flow and state: `SourceDateEpoch` reads the env var, returns nil when unset, and wraps parse errors. `ParseSourceDateEpoch` rejects empty strings, parses an integer Unix timestamp, and returns UTC time. Set/unset mutate process environment.

Dependencies and integration: used by archive diff options and any component requiring reproducible timestamps.

Risks and test signals: environment state is process-global; tests use `t.Setenv` style setup. Negative or huge integer behavior follows `strconv.ParseInt` and `time.Unix`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/epoch/epoch.go -->
