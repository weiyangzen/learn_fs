## sources/cloud-native/moby/daemon/internal/filters/errors.go

Purpose: Defines the package-specific invalid filter error used by filter parsing and validation.

Important API/type: `invalidFilter` carries a filter name and optional values. `Error` formats messages such as `invalid filter` or `invalid filter 'dangling=[bad]'`. `InvalidParameter` marks the error for Docker error classification.

Control flow: Formatting appends the filter name when present and uses `fmt.Sprintf` for values. The marker method is empty and exists for interface detection.

State and persistence: Error values are transient. No persistence.

Dependencies and integration: Integrated by `parse.go` for invalid JSON, unknown filter names, and invalid boolean values. Tests assert both direct type detection and wrapping compatibility through `errors.Is`-style helpers.

Risks: The type is unexported, so external callers rely on marker interfaces and errdefs classification rather than concrete matching. Value slice ordering may be map-dependent unless tests sort expected/actual values.
