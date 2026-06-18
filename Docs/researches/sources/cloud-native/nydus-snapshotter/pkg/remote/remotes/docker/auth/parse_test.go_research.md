# Research: sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/auth/parse_test.go

This test file validates auth challenge parsing. `TestParseAuthHeaderBearer` formats Bearer headers with single and multiple scopes and asserts the parsed challenge preserves realm, service, and scope parameters. `TestParseAuthHeader` verifies an empty quoted parameter is retained and service is parsed correctly. `FuzzParseAuthHeader` seeds a Bearer header and fuzzes arbitrary strings to ensure parsing does not panic.

The tests are good signals for common Docker registry Bearer challenges and parser robustness. They cover quoted parameter values, empty quoted values, and space-containing scope strings. The fuzz test intentionally ignores semantic output and focuses on crash resistance.

Coverage gaps include Basic and Digest ordering, multiple `WWW-Authenticate` headers, escaped quotes/backslashes in values, malformed quoted strings, duplicate keys, unknown schemes, and whitespace edge cases. State is in-memory only. These tests support registry auth flows used by remote resolvers, index detection, and referrer detection.
