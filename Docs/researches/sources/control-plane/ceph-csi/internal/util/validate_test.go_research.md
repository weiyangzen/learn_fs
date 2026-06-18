<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/validate_test.go -->
## sources/control-plane/ceph-csi/internal/util/validate_test.go

Purpose: validates security-sensitive checks for volume IDs and service-account restrictions.

Coverage: dynamic volume IDs with valid prefixes, underscores, long cluster IDs, invalid hex, missing prefixes, special chars, spaces, null byte, Unicode, empty strings, path traversal, and slash/backslash injection. Static volumes skip format but still reject traversal/separators. Service-account tests cover unrestricted, exact match, mismatch, missing pod SA allowed, comma-separated matches, and partial-name rejection.

Dependencies: `testify/require`.

State and integration: pure unit tests; logs may be emitted for missing pod SA cases but are not asserted.

Risks and gaps: does not cover CSI request validator functions or status codes. Does not test whitespace around comma-separated service account values.

Test signal quality: strong for current volume ID hardening and exact SA matching.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/validate_test.go -->
