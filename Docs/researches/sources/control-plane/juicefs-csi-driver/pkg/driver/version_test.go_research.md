# sources/control-plane/juicefs-csi-driver/pkg/driver/version_test.go

Purpose: tests version metadata helpers.

Important APIs and functions: `TestGetVersionJSON` patches `GetVersion` for a normal JSON path and patches `json.MarshalIndent` to force an error. `TestGetVersion` asserts the returned Go runtime version contains `go1.`.

Control flow: GoConvey handles the JSON cases; a standard subtest checks runtime metadata.

State and persistence behavior: no persistent state. Tests use monkey patches of package/global functions.

Dependencies and integration points: depends on gomonkey, GoConvey, `encoding/json`, and runtime behavior.

Risks and test signals: confirms JSON error propagation and basic runtime population. It does not validate linker-injected fields, platform string shape beyond Go version, or `DisableGraceUpgrade` configuration.
