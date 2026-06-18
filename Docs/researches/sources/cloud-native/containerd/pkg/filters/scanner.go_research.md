<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/filters/scanner.go -->
# sources/cloud-native/containerd/pkg/filters/scanner.go

Purpose: lexical scanner for filter syntax.

Important APIs and types: token constants, `token.String`, `token.GoString`, `scanner`, `init`, `next`, `peek`, `scan`, `scanField`, `scanOperator`, `scanValue`, `scanQuoted`, `scanEscape`, `scanDigits`, `error`, and rune classifier helpers.

Control flow and state: scanner tracks current and previous positions, reads runes, emits field/operator/value/separator/quoted/illegal/EOF tokens, and records errors for invalid quotes/escapes. It recognizes field runes, operator runes, separators, quote delimiters, and value characters.

Dependencies and integration: parser depends on token kinds and positions for grammar and error reporting.

Risks and test signals: rune classification defines the accepted filter language. Off-by-one position errors affect user-facing parse messages. `scanner_test.go` provides detailed tokenization cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/filters/scanner.go -->
