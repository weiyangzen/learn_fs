# sources/control-plane/ceph-csi/internal/kms/kmip.go

## Purpose
`kmip.go` registers the KMIP KMS provider. It can either ask a KMIP server to encrypt/decrypt DEKs through KMIP crypto RPCs or fetch a remote symmetric key and perform local AES-GCM encryption for metadata-stored DEKs.

## Important APIs, Types, And Functions
`kmipKMS` stores Kubernetes Secret lookup settings, endpoint, TLS config, unique key identifier, read/write timeouts, and `useCryptoRPC`. `initKMIPKMS()` parses config, Secret certificates, key identifier, TLS server name, and timeout options. Public KMS methods are `EncryptDEK`, `DecryptDEK`, `Destroy`, `RequiresDEKStore`, and `GetSecret`. Internal paths include `encryptDEKUsingEncryptRPC`, `decryptDEKUsingDecryptRPC`, `encryptDEKUsingRemoteKey`, `decryptDEKUsingRemoteKey`, `connect`, `discover`, `send`, `verifyResponse`, `getKey`, `symmetricEncrypt`, and `symmetricDecrypt`.

## Control Flow And State
Initialization builds a TLS 1.2 client config from CA, client certificate, and client key. `connect()` dials the KMIP endpoint, sets deadlines, performs TLS handshake, and verifies KMIP 1.4 support with a DiscoverVersions operation. `send()` constructs a single-batch KMIP request with a UUID batch item ID, TTLV-encodes it, writes to the connection, and decodes the response. `verifyResponse()` validates batch count, operation, batch item ID, and success status. Crypto RPC mode uses KMIP Encrypt/Decrypt with AES-CBC parameters and stores ciphertext plus nonce as JSON. Remote-key mode uses KMIP Get and local AES-GCM with a generated nonce.

## State And Persistence Behavior
The provider requires `DEKStoreMetadata`; encrypted DEK JSON is stored by callers. It does not cache KMIP connections or fetched keys. TLS and key identifiers stay in memory. `Destroy()` is no-op.

## Dependencies And Integration Points
The implementation uses `gemalto/kmip-go`, TLS/x509, Go crypto primitives, JSON encoding, Kubernetes Secrets, and helper functions from `kms_util.go`, `vault.go`, and `secretskms.go`.

## Risks And Edge Cases
KMIP operation support varies by server. The local-key mode exposes raw symmetric key material to the CSI process after a KMIP Get. Timeout config is parsed as int but stored as `uint8`, so large values can wrap. `AppendCertsFromPEM` return value is not checked. Crypto RPC mode uses AES-CBC with PKCS5 padding via the KMIP service, while local mode uses AES-GCM, so ciphertext formats are mode-specific. Network and KMIP response validation are only as strict as the decoded fields.

## Test Signals
`kmip_test.go` only checks registration. There is no coverage for TLS config validation, DiscoverVersions, TTLV request/response handling, crypto RPCs, local AES-GCM helpers, timeout conversion, malformed encrypted JSON, or KMIP error status mapping.
