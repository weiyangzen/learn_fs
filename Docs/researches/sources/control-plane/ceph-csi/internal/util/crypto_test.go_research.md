<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/crypto_test.go -->
## sources/control-plane/ceph-csi/internal/util/crypto_test.go

**Purpose:** Tests passphrase generation, the default KMS encryption workflow, and encryption type parsing.

**Important APIs and functions:** `TestGenerateNewEncryptionPassphrase` decodes the base64 output and checks byte length. `TestKMSWorkflow` creates the default KMS from a secret, creates `VolumeEncryption`, stores a new passphrase, and reads it back. `TestFetchEncryptionType` checks fallback, empty invalid value, block/file strings, and invalid strings.

**Control flow, state, and persistence:** Tests are parallel and mostly in-memory. The KMS workflow uses the test/default KMS behavior rather than real external KMS state.

**Dependencies and integration points:** Depends on `testify/require`, internal KMS, and package crypto enum types. It protects controller option parsing and KMS integration at a unit level.

**Risks and test signals:** It does not cover `FetchEncryptionKMSID`, missing DEK store errors, LUKS mapper helpers, cryptsetup status parsing, or command execution paths. The default KMS test relies on provider-specific semantics where the fetched passphrase equals the configured secret.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/crypto_test.go -->
