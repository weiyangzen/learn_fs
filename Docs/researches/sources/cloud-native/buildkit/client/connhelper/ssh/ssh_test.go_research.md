# sources/cloud-native/buildkit/client/connhelper/ssh/ssh_test.go

Purpose: unit tests for SSH connection-helper URL parsing.

Important APIs/types/functions: `TestSpecFromURL` covers host-only URLs, user/port/socket paths, password rejection, socket-only path, query rejection, fragment rejection, and missing host rejection.

Control flow: table-driven parse/assert loop follows the same pattern as the container helpers.

State and persistence: none.

Dependencies/integration points: `net/url`, testing, and `testify/require`.

Risks/test signals: confirms parser security and ambiguity checks. It does not cover generated SSH command argument ordering or remote command behavior.
