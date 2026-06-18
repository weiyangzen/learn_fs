<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/sshutil/scpurl_test.go -->
# sources/cloud-native/buildkit/util/sshutil/scpurl_test.go

Purpose: validates implicit SCP-style SSH URL detection and parsing.

Important APIs and types: `TestIsImplicitSSHTransport` and `TestParseSCPStyleURL`.

Control flow: detection tests assert false for HTTP, plain host/path, malformed, and explicit SSH URLs, and true for common and unusual username/path SCP forms. Parse tests assert failure for non-SCP inputs and field extraction for simple and fragment-bearing SCP URLs.

State and persistence: pure table tests.

Dependencies and integration: uses `testify/require`.

Risks: tests do not cover query parsing or `SCPStyleURL.String` round trips.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/sshutil/scpurl_test.go -->
