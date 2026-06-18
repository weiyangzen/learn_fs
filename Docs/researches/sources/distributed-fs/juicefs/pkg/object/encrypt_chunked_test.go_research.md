# sources/distributed-fs/juicefs/pkg/object/encrypt_chunked_test.go


Purpose: regression-tests concurrent reads from chunked encrypted storage.

Important APIs and flow: `TestChunkedEncryptedConcurrentGet` creates a memory store, builds an RSA/AES-GCM `dataEncryptor`, wraps it with `NewChunkedEncrypted`, writes a deterministic 1024-byte object, then launches 30 goroutines. Each goroutine calls `Get` for the whole object and reads one byte at a time before comparing against the original content.

State and persistence: data persists only in the in-memory backend for the test duration. The concurrency pressure targets per-reader buffer state and wrapper-level sync pools.

Dependencies and integration: depends on `rsaKey` from `encrypt_test.go`, `CreateStorage("mem", ...)`, `NewDataEncryptor`, `NewRSAEncryptor`, and testify `require`.

Risks and gaps: the test uses only one small object, one algorithm, and whole-object reads. It does not cover cross-chunk ranges, corrupt chunk headers, multipart upload behavior, or filesystem interface preservation.

Test signal: strong for the specific race/aliasing class where `chunkDecryptReader` retains slices backed by pooled encrypted buffers while many readers are active.
