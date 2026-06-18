# sources/control-plane/juicefs-csi-driver/pkg/driver/version.go

Purpose: exposes build and runtime version metadata for the CSI driver.

Important APIs and types: build-time variables `driverVersion`, `gitCommit`, and `buildDate` are intended to be set by linker flags. `VersionInfo` serializes driver version, commit, build date, Go runtime version, compiler, platform, and `config.DisableGraceUpgrade`. `GetVersion` populates the struct from globals, `runtime`, and config. `GetVersionJSON` returns an indented JSON string.

Control flow: `GetVersionJSON` calls `GetVersion`, marshals with `json.MarshalIndent`, and returns the string or marshal error.

State and persistence behavior: no state is mutated or persisted. It reads process-global version/config values.

Dependencies and integration points: used by CLI/logging paths that need version output. Depends on `runtime`, `encoding/json`, `fmt`, and driver config.

Risks and test signals: zero-value build variables produce empty version fields in local/test builds. The JSON marshal path is straightforward; tests patch marshal errors and assert Go version formatting.
