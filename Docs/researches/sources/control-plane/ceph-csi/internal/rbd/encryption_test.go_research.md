# sources/control-plane/ceph-csi/internal/rbd/encryption_test.go

## Purpose
Unit-tests the pure parsing layer for RBD encryption options: whether encryption is enabled, how KMS IDs and encryption types are resolved, and how cryptsetup cipher options are accepted or rejected.

## Important APIs, Types, And Functions
`TestParseEncryptionOpts` checks missing `encrypted`, false values, invalid booleans, and a valid KMS ID. `TestParseCipherOptions` checks nil options when no cipher is provided, allowed AES-XTS settings, integrity/key-size/sector-size handling, and rejection of unsafe AES-GCM style configuration. `valueToPointer` helps construct expected option fields.

## Control Flow
Both tests are table-driven and parallel. `TestParseCipherOptions` constructs an expected `cryptsetup.EncryptionOptions` using the same setter APIs used by production code, then compares the resulting struct to the parser output.

## State And Persistence
No external or persistent state is used. The tests do not instantiate KMS backends, RBD images, device mappings, or metadata.

## Dependencies And Integration Points
The file depends on `cryptsetup.EncryptionOptions`, `crypto.EncryptionType`, and `testify` assertions. It validates the front door used by `initKMS` before controller create proceeds.

## Risks And Test Signals
The tests are strong signals for rejecting invalid encryption configuration before resource creation. Coverage gaps include `configureBlockEncryption`, file encryption KMS compatibility, DEK storage, metadata migration, LUKS formatting/opening, and key rotation failure handling.
