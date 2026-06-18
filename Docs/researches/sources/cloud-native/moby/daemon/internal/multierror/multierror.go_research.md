<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/multierror/multierror.go -->
# sources/cloud-native/moby/daemon/internal/multierror/multierror.go

Purpose: joins multiple errors like `errors.Join` but formats multi-error messages as bullet lists with indentation.

Important APIs and types: `Join`, `joinError`, `Error`, and `Unwrap`.

Control flow: `Join` filters nil errors, returns nil if none, and returns a `joinError`. `Error` returns the trimmed single error when only one error exists; for multiple errors it prefixes each error with `* ` and indents embedded newlines. `Unwrap` exposes the slice for `errors.Is/As`.

State and persistence: immutable in-memory slice of errors.

Dependencies and integration: used where user-facing configuration or validation errors need better formatting while preserving multi-error unwrapping.

Risks: formatting is intentionally different from Go stdlib joins, so callers comparing exact strings must account for bullets. Single-error trimming can remove meaningful surrounding whitespace.

Test signals: `multierror_test.go` covers single nested and multiple nested formatting.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/multierror/multierror.go -->
