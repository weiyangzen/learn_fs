# sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_c.go

## Purpose
`s3_sse_c.go` implements SSE-C support for customer-provided AES-256 keys. It parses and validates request headers, creates AES-CTR encrypt/decrypt readers, supports offset-aware CTR streams, decides copy strategies, and maps SSE-C errors to S3 errors.

## Important APIs, Types, and Functions
Core types are `SSECustomerKey`, `SSECCopyStrategy`, and `decryptReaderCloser`. Key functions include `IsSSECRequest`, `IsSSECEncrypted`, `ParseSSECHeaders`, `ParseSSECCopySourceHeaders`, `CreateSSECEncryptedReader`, `CreateSSECDecryptedReader`, `CreateSSECEncryptedReaderWithOffset`, `CreateSSECDecryptedReaderWithOffset`, `GetSourceSSECInfo`, `CanDirectCopySSEC`, `DetermineSSECCopyStrategy`, `createCTRStreamWithOffset`, and `MapSSECErrorToS3Error`.

## Control Flow
SSE-C header parsing requires algorithm, key, and key-MD5 to appear together. The algorithm must be `AES256`; the key must base64-decode to 32 bytes; the provided MD5 must match the base64 MD5 of the raw key. Encryption creates an AES block with the customer key, generates a random 16-byte IV, and wraps the source reader in a CTR stream. Decryption validates the metadata IV, creates the same CTR stream, and preserves close behavior when the input reader is an `io.Closer`. Offset variants derive an adjusted IV and discard intra-block keystream bytes through `calculateIVWithOffset`.

## State and Persistence Behavior
The raw customer key is never stored by this file. Persistent metadata elsewhere stores the SSE-C algorithm, key MD5, and IV. Copy decisions use source metadata and request-provided source/destination keys but do not mutate state.

## Dependencies and Integration Points
The file depends on AES/CTR, MD5, base64, S3 constants/errors, and shared IV validation/offset helpers. It integrates with object PUT/GET/copy paths, metadata helpers, and multipart chunk encryption.

## Risks and Edge Cases
AES-CTR provides confidentiality but not authentication; the broader SSE implementation mitigates key/IV confusion with commitments only for some paths. Key MD5 is an identifier/checksum, not a secret. `IsSSECRequest` treats KMS headers as mutually exclusive and ignores malformed mixes by returning false, so caller validation must catch invalid combinations. Direct copy is allowed only when source and destination key MD5s match the stored source MD5; collision risk is theoretical but MD5 is still not collision-resistant.

## Test Signals
High-value tests include complete/missing header combinations, wrong algorithm, wrong key length, MD5 mismatch, encrypt/decrypt round trips, IV validation, offset decrypt reads, copy strategy errors, and error-to-S3-code mapping.
