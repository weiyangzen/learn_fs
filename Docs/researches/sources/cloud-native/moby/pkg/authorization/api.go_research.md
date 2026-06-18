<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/authorization/api.go -->
# sources/cloud-native/moby/pkg/authorization/api.go

Purpose: defines the wire contract between dockerd and authorization plugins. Important API constants are `AuthZApiRequest`, `AuthZApiResponse`, and `AuthZApiImplements`; important types are `PeerCertificate`, `Request`, and `Response`. Control flow is limited to JSON marshaling/unmarshaling of peer certificates as PEM bytes; request/response structs carry user identity, HTTP method/URI/body/headers, TLS certs, response status, and plugin allow/deny messages. State is serialized JSON exchanged with plugins. Dependencies include x509, PEM, and JSON encoding. Risks include `UnmarshalJSON` assuming `pem.Decode` succeeds before dereferencing, sensitive header/body exposure, and compatibility with plugin field names. Test signal is `api_test.go` certificate round-trip coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/authorization/api.go -->
