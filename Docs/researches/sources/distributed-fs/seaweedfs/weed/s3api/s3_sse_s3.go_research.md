# sources/distributed-fs/seaweedfs/weed/s3api/s3_sse_s3.go

## Purpose
`s3_sse_s3.go` implements SSE-S3 server-managed encryption. It generates per-object or per-chunk data encryption keys, encrypts object data with AES-CTR, stores encrypted DEKs in metadata under a key-encryption key, manages KEK loading/configuration/migration, and initializes the global SSE-S3 key manager.

## Important APIs, Types, and Functions
Important types are `SSES3Key`, `SSES3KeyManager`, and `KeyManagerFilerClient`. Important functions include `IsSSES3RequestInternal`, `IsSSES3EncryptedInternal`, `GenerateSSES3Key`, `CreateSSES3EncryptedReader`, `CreateSSES3DecryptedReader`, `SerializeSSES3Metadata`, `DeserializeSSES3Metadata`, `NewSSES3KeyManager`, `SetKEKPassphrase`, `InitializeWithFiler`, `loadSuperKeyFromFiler`, `wrapKEK`, `unwrapKEK`, `deriveWrappingKey`, `deriveKeyFromSecret`, `encryptKeyWithSuperKey`, `decryptKeyWithSuperKey`, `GetMasterKey`, `InitializeGlobalSSES3KeyManager`, `GetSSES3IV`, and `CreateSSES3EncryptedReaderWithBaseIV`.

## Control Flow
Encryption generates a 32-byte DEK and random IV, encrypts data using AES-CTR, and serializes metadata by encrypting the DEK with the manager's KEK using AES-GCM. Metadata includes algorithm, key ID, encrypted DEK, nonce, optional IV, and key commitment. Decryption deserializes metadata, decrypts the DEK through the key manager, validates IV and commitment, and returns a decrypting reader.

`InitializeWithFiler` resolves the KEK from config or filer in priority order: hex `s3.sse.kek`, derived `s3.sse.key`, existing filer KEK, or disabled SSE-S3. It refuses conflicting config, checks config KEK against existing filer KEK when reachable, refuses derived keys while a filer KEK exists, and migrates passphrase-wrapped legacy formats toward salted v2 wrapping. The global initializer wires a `wdclient.FilerClient` adapter and reads the KEK passphrase from Viper or environment.

## State and Persistence Behavior
The key manager stores the active KEK in memory under a mutex. Filer-backed KEKs live at `/etc/s3/sse_kek`, possibly plaintext hex for legacy deployments or passphrase-wrapped AES-GCM payloads. Object metadata stores encrypted DEKs and IV/commitment data. No plaintext DEKs are stored persistently.

## Dependencies and Integration Points
The file depends on AES/CTR/GCM, HKDF-SHA256, Viper config helpers, filer protobuf clients, wdclient, gRPC, S3 constants, and shared validation/commitment helpers. It integrates with S3 PUT/GET/copy handlers and with STS via `GetMasterKey`.

## Risks and Edge Cases
`GenerateSSES3Key` uses `math/rand.Int63` for key IDs, which are identifiers not keys but can collide. SSE-S3 is disabled silently at init when no KEK exists; first encrypt/decrypt returns an error. Legacy plaintext KEK support is upgrade-friendly but sensitive; warning visibility matters. `IsSSES3EncryptedInternal` requires both algorithm header and encrypted key metadata, preventing stale-header false positives. Correct multipart decryption depends on per-chunk metadata validation and IV handling.

## Test Signals
Tests cover inline and chunked end-to-end flows, per-chunk key decryption, invalid IV failure before fetch, passphrase wrapping round trips and random salts, CTR offset behavior, and type detection. Additional coverage should exercise config/filer KEK conflict handling and disabled SSE-S3 errors.
