# sources/distributed-fs/beegfs-go/common/strfmt/strfmt.go

Purpose: package-level string formatting helpers used for human-readable BeeGFS Go output.

Important API is `CapitalizeFirst(s string) string`. It decodes the first UTF-8 rune, uppercases it with Unicode rules, and appends the untouched remainder.

Control flow is minimal: empty strings return unchanged; non-empty strings use `utf8.DecodeRuneInString` and `unicode.ToUpper`.

State and persistence: none. Dependencies are `unicode` and `unicode/utf8`.

Integration points are output formatting code that wants capitalization without assuming ASCII-only input.

Risks: invalid UTF-8 decodes to `utf8.RuneError` and will be uppercased/re-emitted, which may change the byte sequence. Only the first rune is capitalized; locale-specific casing is not handled beyond Go's Unicode tables.

Test signals: no direct tests for `CapitalizeFirst` in this subset. The time formatting functions in the same package have tests.
