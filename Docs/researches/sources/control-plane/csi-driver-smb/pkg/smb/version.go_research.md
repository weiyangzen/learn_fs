<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/version.go -->
# sources/control-plane/csi-driver-smb/pkg/smb/version.go

Purpose: Defines build-time version metadata and renders it as structured `VersionInfo` or YAML for startup logging.

Important APIs/types/functions: Build variables `driverVersion`, `gitCommit`, and `buildDate` default to `N/A` and are intended for `-ldflags` injection. `VersionInfo` includes driver name/version, git commit, build date, Go version, compiler, and platform. `GetVersion` fills runtime fields from `runtime`. `GetVersionYAML` marshals the struct with `sigs.k8s.io/yaml` and trims surrounding whitespace.

Control flow: Version retrieval is pure except YAML marshaling error handling. `Run` in `smb.go` fatal-exits if YAML marshaling fails, which should be unlikely for this static struct.

State and persistence behavior: No persistence; state is process build metadata and runtime introspection.

Dependencies and integration points: Used by driver startup logs and tests. Build/release scripts can inject variable values to make images auditable.

Risks: Missing ldflags leave version fields as `N/A`, reducing operational traceability. JSON tags include spaces in field names, which controls YAML output labels but may surprise consumers expecting Go-style keys.

Test signals: `version_test.go` checks default values and YAML equivalence with the same marshaler.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/version.go -->
