<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/filters/parser.go -->
# sources/cloud-native/containerd/pkg/filters/parser.go

Purpose: recursive-descent parser for containerd filter expressions.

Important APIs and types: `Parse`, `ParseAll`, internal `parser`, `selectors`, `selector`, `fieldpath`, `field`, `operator`, `value`, `unquote`, `parseError`, and `mkerr`.

Control flow and state: empty input returns `Always`. `ParseAll` parses multiple independent filter strings and wraps them in `Any`. The parser consumes scanner tokens for comma-separated selectors, dot-separated field paths, optional operators, and values. Regex-match values allow alternate quote delimiters; field names do not.

Dependencies and integration: uses `scanner.go` for tokens, `quote.go` for unquoting, and wraps errors with `errdefs.ErrInvalidArgument` in `ParseAll`.

Risks and test signals: error messages include input position and are asserted in tests, so changes are compatibility-sensitive. Hand-written parsing must stay aligned with scanner tokenization.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/filters/parser.go -->
