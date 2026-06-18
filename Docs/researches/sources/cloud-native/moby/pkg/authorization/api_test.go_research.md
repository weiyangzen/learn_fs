<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/authorization/api_test.go -->
# sources/cloud-native/moby/pkg/authorization/api_test.go

Purpose: validates JSON PEM round-tripping for `PeerCertificate`. The test creates an RSA key, a self-signed x509 certificate with subject/key-usage fields, marshals through `PeerCertificate`, unmarshals, and compares selected certificate properties. State is temporary in-memory certificate data. Dependencies include crypto/x509, RSA, TLS-related structures, and gotest assertions. Risks covered include losing certificate metadata or malformed PEM generation; risks not covered include invalid PEM error handling. Test signal is focused on plugin API compatibility for TLS peer certificates.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/authorization/api_test.go -->
