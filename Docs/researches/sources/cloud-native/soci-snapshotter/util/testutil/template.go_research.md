# sources/cloud-native/soci-snapshotter/util/testutil/template.go

## Purpose
`template.go` provides helpers for applying Go text templates in tests.

## Important APIs, Types, and Functions
`ApplyTextTemplate(temp, config)` wraps `ApplyTextTemplateErr` and returns a string. `ApplyTextTemplateErr(temp, conf)` creates a template named by the digest of the template source, parses it with `template.Must`, executes it into a bytes buffer, and returns the bytes.

## Control Flow, State, and Persistence
The functions are stateless. Parse failures panic due to `template.Must`; execution failures are returned by `ApplyTextTemplateErr` and wrapped without preserving the original error in `ApplyTextTemplate`.

## Dependencies and Integration Points
Dependencies are `bytes`, `fmt`, `text/template`, and `go-digest`. The digest-derived name avoids conflicts and gives deterministic template names.

## Risks and Test Signals
`ApplyTextTemplate` discards the underlying execution error when wrapping, reducing diagnostics. Parse errors panic rather than returning an error, so callers must only pass trusted test templates.
