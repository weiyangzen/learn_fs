<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/filters/filter_test.go -->
# sources/cloud-native/containerd/pkg/filters/filter_test.go

Purpose: broad behavioral tests for parsing and applying filter expressions.

Important APIs and functions: `TestFilters`, `TestOperatorStrings`, and `FuzzFiltersParse`.

Control flow and state: table tests parse filter strings, build adaptors over test maps/field paths, compare matched results, and verify error strings for malformed input. Operator string tests validate debug formatting. Fuzzing asserts parse never returns both nil filter and nil error.

Dependencies and integration: tests cover parser, scanner, quote handling, selector matching, and adaptor behavior together.

Risks and test signals: the table is the main compatibility contract for filter syntax, including quoted field labels, regex delimiters, separators, and invalid forms.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/filters/filter_test.go -->
