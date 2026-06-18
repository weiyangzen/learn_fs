<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolver/utils.go -->
# sources/cloud-native/buildkit/util/resolver/utils.go

Purpose: parses registry mirror strings into host and optional path components.

Important APIs and types: `extractMirrorHostAndPath`.

Control flow: attempts to parse the mirror as a URL; if no host is present, retries by prepending `//` so bare `host/path` strings parse as authority plus path. Returns the original string and empty path if parsing still fails. Path is trimmed of trailing slash.

State and persistence: pure string transformation.

Dependencies and integration: used by `newMirrorRegistryHost` to build mirror `docker.RegistryHost` values.

Risks: malformed but URL-parseable input may produce surprising host/path splits; validation is left to subsequent registry client behavior.

Test signals: covered indirectly by `resolver_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolver/utils.go -->
