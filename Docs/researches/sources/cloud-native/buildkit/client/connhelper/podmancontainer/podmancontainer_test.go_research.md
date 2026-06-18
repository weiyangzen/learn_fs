# sources/cloud-native/buildkit/client/connhelper/podmancontainer/podmancontainer_test.go

Purpose: unit tests for Podman container URL parsing.

Important APIs/types/functions: `TestSpecFromURL` verifies a valid container host and rejects an empty host.

Control flow: parse string, call `SpecFromURL`, require equality or error based on expected table entry.

State and persistence: none.

Dependencies/integration points: `net/url`, testing, and `testify/require`.

Risks/test signals: confirms minimal parse contract; does not test command execution, path handling, or unsupported query parameters.
