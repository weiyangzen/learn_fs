# sources/distributed-fs/juicefs/pkg/object/encrypt_chunked.go


Purpose: provides chunked object encryption that preserves practical range reads and plaintext size reporting.

Important APIs and flow: `NewChunkedEncrypted` wraps an `ObjectStorage` with 1 MiB plaintext chunks. Each stored chunk has a 4-byte big-endian ciphertext-length header followed by encrypted data padded to a fixed encrypted chunk size. `Get` maps plaintext offset/limit to encrypted chunk offset/limit, then returns `chunkDecryptReader`, which decrypts chunk by chunk, skips the initial plaintext offset, and optionally limits output. `Put` streams plaintext through `chunkEncryptReader`, which encrypts each chunk and emits fixed-size records. `Head`, `List`, and `ListAll` wrap returned objects with recalculated plaintext size. Multipart upload encrypts each part stream and disables upload-part-copy.

State and persistence: stored object layout is chunk records; no external metadata is required for size reconstruction. Pools hold plaintext and encrypted chunk buffers per wrapper.

Dependencies and integration: uses `dataEncryptor`, `FileSystem`, `SupportSymlink`, `SupportTier`, and shared `ObjectStorage` methods. It preserves filesystem and symlink interfaces by embedding wrappers when possible.

Risks: `calcPlainSize` is an inference from encrypted size and fixed overhead; malformed/corrupt objects can produce misleading sizes before read-time errors. Each encrypted chunk has fresh key material due to `dataEncryptor.Encrypt`, increasing overhead and CPU cost. `UploadPart` buffers the encrypted part in memory. Small or truncated chunks surface decryption errors during reads.

Test signals: `encrypt_chunked_test.go` stresses concurrent reads and one-byte read patterns to catch buffer aliasing.
