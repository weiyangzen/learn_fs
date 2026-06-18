# sources/cloud-native/soci-snapshotter/internal/http/util_test.go

Purpose: tests and benchmarks for HTTP query redaction helpers.

Important APIs/types/functions: `TestRedactHTTPQueryValuesFromError`, `TestRedactHTTPQueryValuesFromURL`, and `BenchmarkRedactHTTPQueryValuesOverhead`. Constants model an S3-like URL with sensitive username/password query values and expected sorted redacted query output.

Control flow: table-driven tests feed nil errors, non-URL errors, URL errors with and without query strings, nil URLs, empty URLs, and raw query maps into redaction utilities. The benchmark compares baseline log writes against redaction with and without replacement.

State and persistence: no persistent state; tests mutate URL and error objects in-memory.

Dependencies/integration points: uses `logrus.Entry` with an in-memory buffer to measure logging overhead. Mirrors resolver error-redaction behavior.

Risks: expected query order depends on `url.Values.Encode` sorting keys. Tests do not cover malformed URL strings for `RedactHTTPQueryValuesFromString` or nil body behavior for `Drain`.

Test signals: confirms sensitive values are replaced with `redacted`, unrecognized errors are unchanged, and redaction has benchmark coverage for performance tracking.
