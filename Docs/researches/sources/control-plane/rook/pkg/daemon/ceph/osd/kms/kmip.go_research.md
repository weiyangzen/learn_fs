# sources/control-plane/rook/pkg/daemon/ceph/osd/kms/kmip.go

This file implements a KMIP 1.4 KMS backend over mutual TLS.

`InitKMIP()` validates endpoint, CA cert, client cert, and client key; reads optional TLS server name and read/write timeouts; bounds timeout values to `uint8`; builds a CA pool and client certificate; and creates a TLS config requiring TLS 1.2 or newer. `kmipKMS` methods implement secret lifecycle: `registerKey()` base64-decodes a value and registers it as an AES symmetric key with export usage; `getKey()` retrieves a symmetric key and returns base64; `deleteKey()` destroys an identifier. `connect()` opens TLS, sets deadlines, handshakes, and runs KMIP discover. `discover()` validates protocol version 1.4. `send()` TTLV-marshals a one-item request with a UUID batch ID, writes it, reads and decodes the response. `verifyResponse()` enforces one batch item, expected operation, matching batch ID, and success status.

State is remote KMIP server key material plus transient TLS connections. Dependencies include `gemalto/kmip-go`, TTLV encoding, TLS/x509, UUIDs, and base64. Risks include a likely write-timeout bug using `SetReadDeadline` instead of `SetWriteDeadline`, type assertions on response payload/key material, no retry logic, and strict one-version discovery. `kmip_test.go` covers missing required config only.
