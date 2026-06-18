<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/filters/quote.go -->
# sources/cloud-native/containerd/pkg/filters/quote.go

Purpose: modified Go string unquoting implementation that also supports `/` and `|` delimiters for regular expression filter values.

Important APIs and functions: `unquoteChar`, `unquote`, `unhex`, `contains`, and package error `errQuoteSyntax`.

Control flow and state: decodes escapes for simple, hex, Unicode, octal, and quoted characters; rejects invalid quote syntax and invalid Unicode. Alternate quote delimiters are treated like double quotes for regex-focused parsing.

Dependencies and integration: used by parser `unquote` when processing quoted fields/values. The implementation is adapted from Go's `strconv` logic.

Risks and test signals: quote behavior is syntax-critical and security-adjacent because filters may include arbitrary labels and regexes. Scanner/parser tests cover valid/invalid escape forms.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/filters/quote.go -->
