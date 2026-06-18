# sources/control-plane/ceph-csi/e2e/errors_test.go

Purpose: unit-tests the kubectl stderr extraction and AlreadyExists classification helpers from `errors.go`.

Important APIs/types/functions: `TestGetStdErr(t)` defines table-driven cases with formatted kubectl output and checks both `getStdErr()` and `isAlreadyExistsCLIError()`.

Control flow: the test runs in parallel and each subtest also runs in parallel. Cases cover normal output containing `stderr:` and `error:` delimiters with two AlreadyExists server errors, output missing `stderr:`, and output missing the trailing `error:` delimiter. For each case it compares the extracted stderr string and the AlreadyExists boolean.

State and persistence: no external state; all data is inline sample text.

Dependencies and integration points: uses Go `testing` and `fmt.Errorf()` to wrap sample strings into errors. It directly exercises the helper contract used by kubectl retry logic elsewhere in the e2e package.

Risks: coverage is narrow: NotFound, no-such-resource, warnings, blank-line-only stderr, mixed errors, and retryable API predicates are not unit-tested here. Parallel subtests are safe because helpers are pure.

Test signals: passing tests confirm the current kubectl wrapper format is parsed as expected and that missing delimiters produce empty stderr plus false classification.
