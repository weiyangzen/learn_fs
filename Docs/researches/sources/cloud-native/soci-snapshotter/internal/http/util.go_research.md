# sources/cloud-native/soci-snapshotter/internal/http/util.go

Purpose: HTTP utility functions for redacting sensitive query values from URLs/errors and draining response bodies for connection reuse.

Important APIs/types/functions: `RedactHTTPQueryValuesFromError` detects `*url.Error`, parses its URL, redacts query values, and mutates `urlErr.URL`. `RedactHTTPQueryValuesFromURL` replaces every query value with `redacted`. `RedactHTTPQueryValuesFromString` parses and redacts a URL string. `Drain` reads up to 4 KiB from a response body and closes it.

Control flow: redaction functions parse or inspect URL values, mutate in place when possible, and leave invalid/non-URL errors unchanged. Drain defers close and copies from a limited reader to `io.Discard`.

State and persistence: no package state, but functions mutate passed URL objects and `*url.Error` values.

Dependencies/integration points: resolver retry/error handling uses these functions to avoid leaking credentials or pre-signed URL tokens in logs and errors. Auth replay uses `Drain` before resending after challenge.

Risks: redaction preserves query keys, which can still reveal parameter names. `RedactHTTPQueryValuesFromError` mutates the original `url.Error`, which can surprise callers holding the same error. `Drain` assumes non-nil body; callers must guard when responses can have nil body.

Test signals: companion tests cover nil/non-URL errors, no-query URLs, query redaction, nil URL handling, and benchmark logging overhead.
