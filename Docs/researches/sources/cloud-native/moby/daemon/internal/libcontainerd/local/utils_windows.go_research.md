<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/local/utils_windows.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/local/utils_windows.go

Purpose: converts OCI-style environment string slices into the map form required by HCS.

Important APIs and types: `setupEnvironmentVariables(a []string) map[string]string`.

Control flow: iterates each string, splits once on the first `=`, and records key/value pairs only when a separator exists. Values may contain further `=` characters.

State and persistence: creates a fresh map and has no persistent state. Duplicate keys are overwritten by the last value seen.

Dependencies and integration: used by `local_windows.go` for both initial task and exec process `hcsshim.ProcessConfig.Environment`.

Risks: entries without `=` are silently dropped. Empty keys are accepted if present in input. Duplicate key behavior is implicit map overwrite.

Test signals: `utils_windows_test.go` verifies normal entries and values containing `=`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/local/utils_windows.go -->
