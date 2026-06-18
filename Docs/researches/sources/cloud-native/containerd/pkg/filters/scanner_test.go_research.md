<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/filters/scanner_test.go -->
# sources/cloud-native/containerd/pkg/filters/scanner_test.go

Purpose: tests for tokenization of valid and invalid filter strings.

Important APIs and functions: `TestScanner` drives scanner initialization and repeated `scan` calls over table cases.

Control flow and state: each case supplies an input and expected token sequence; the test scans until EOF or illegal token, asserts token/text/position expectations, and fails if input is not consumed or expected tokens are absent.

Dependencies and integration: directly validates scanner behavior independent from parser, giving precise coverage for quotes, escapes, separators, values, fields, and operators.

Risks and test signals: protects grammar compatibility. Any change to accepted characters or quote handling should update both scanner and parser tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/filters/scanner_test.go -->
