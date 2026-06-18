# sources/cloud-native/buildkit/client/connhelper/nerdctlcontainer/nerdctlcontainer_test.go

Purpose: unit tests for nerdctl container helper URL parsing.

Important APIs/types/functions: `TestSpecFromURL` validates `nerdctl-container://containername` and rejects `nerdctl-container://`.

Control flow: parses each URL, calls `SpecFromURL`, and asserts either equality or error.

State and persistence: none.

Dependencies/integration points: `net/url`, testing, and `testify/require`.

Risks/test signals: confirms required container host handling. It does not currently test `namespace` query parsing, unknown query handling, or helper command construction.
