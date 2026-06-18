<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/multierror/multierror_test.go -->
# sources/cloud-native/moby/daemon/internal/multierror/multierror_test.go

Purpose: verifies custom multi-error formatting.

Important APIs and types: `TestErrorJoin` covers `Join`.

Control flow: subtest `single` wraps one joined error and expects no bullet formatting. Subtest `multiple` joins a plain error with a nested multi-error and expects bullet/indent formatting.

State and persistence: none.

Dependencies and integration: uses `gotest.tools/assert`.

Risks: exact string tests are sensitive to formatting changes, but that is the contract of this package.

Test signals: confirms newline indentation and single-error trimming behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/multierror/multierror_test.go -->
