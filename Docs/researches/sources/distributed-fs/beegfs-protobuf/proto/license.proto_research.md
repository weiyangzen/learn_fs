# sources/distributed-fs/beegfs-protobuf/proto/license.proto

**Purpose:** This proto defines license and certificate result messages used to pass structured data from a Go library to consumers, including consumers crossing a C FFI boundary through serialized C strings. It models verification outcomes, certificate categories, feature checks, and simplified x509 certificate data.

**Important APIs/types/functions:** Enums are `VerifyResult` (`VERIFY_ERROR`, `VERIFY_VALID`, `VERIFY_INVALID`) and `CertType` (`CA_ROOT`, `CA_INTERMEDIATE`, `PARTNER`, `ENTERPRISE`, `TRIAL`, `COMMUNITY`). Result messages include `VerifyCertResult`, `VerifyFeatureResult`, and `GetCertDataResult`. `CertData` carries certificate type, numeric serial, subject fields, common/subject serial strings, validity timestamps, DNS names with JSON name `DNSNames`, `is_ca`, and optional recursive `parent_data`.

**Control flow:** Library code verifies a certificate or feature and serializes the corresponding result message. Consumers inspect `result` first, then either read `serial`/`data` for successful or partially available results, or read `message` for errors/invalid reasons. `GetCertDataResult` can include certificate data even when verification failed.

**State and persistence behavior:** Certificate state is a simplified x509 projection rather than full certificate bytes. Validity uses protobuf timestamps. DNS names encode licensed features such as feature names or quantity-like names. `parent_data` recursively embeds issuer information, so consumers should handle nested certificate chains. The schema preserves result distinctions between operational errors and verification invalidity.

**Dependencies and integration points:** Imports `google/protobuf/timestamp.proto`. Management generated code depends on `license.GetCertDataResult` for `GetLicenseResponse`. The comments explicitly target Go library output and language-agnostic FFI consumers.

**Risks:** This schema does not carry raw signatures, public keys, or full x509 extensions, so it is suitable for reporting, not independent cryptographic verification. Recursive `parent_data` can create large payloads if chains are long. DNS names as feature identifiers require consistent naming conventions outside the proto. Consumers must not treat `data` presence alone as proof of validity; `result` controls meaning.

**Test signals:** Tests should cover valid, invalid, and error results; serialization across C FFI boundaries; JSON mapping for `DNSNames`; timestamp round trips; parent chain nesting; and management `GetLicense` responses with reload true/false. Verification tests should assert that invalid certificates carry useful messages and that failed verification can still return available certificate data where intended.
