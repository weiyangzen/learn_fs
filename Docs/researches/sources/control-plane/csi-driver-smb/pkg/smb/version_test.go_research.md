<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/version_test.go -->
# sources/control-plane/csi-driver-smb/pkg/smb/version_test.go

Purpose: Unit tests for version metadata rendering.

Important APIs/functions: `TestGetVersion` compares `GetVersion(DefaultDriverName)` with expected default build values plus runtime Go/compiler/platform values. `TestGetVersionYAML` marshals `GetVersion("")` independently and compares trimmed YAML output with `GetVersionYAML("")`.

Control flow: Both tests are straightforward direct assertions.

State and persistence behavior: None; tests read runtime metadata only.

Dependencies and integration points: Uses `runtime`, `sigs.k8s.io/yaml`, `reflect`, and package constants. It protects startup log metadata consumed by `Driver.Run`.

Risks: The tests assume build variables remain at default `N/A` in unit test builds; a test environment that injects ldflags could require adjusted expectations.

Test signals: Good signal for default metadata shape and YAML serialization; no error-path coverage because marshaling the struct is expected to be stable.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/pkg/smb/version_test.go -->
