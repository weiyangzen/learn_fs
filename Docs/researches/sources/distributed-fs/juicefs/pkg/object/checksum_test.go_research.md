# sources/distributed-fs/juicefs/pkg/object/checksum_test.go


Purpose: validates the checksum helpers in `checksum.go`.

Important APIs and flow: `TestChecksum` computes the expected CRC32C of `"hello"` and checks repeated `generateChecksum(bytes.NewReader(...))` calls, including the seek-back behavior. `TestChecksumRead` generates random 10 KiB content, wraps it through `verifyChecksum`, and exercises exact-size reads, oversized buffers, corrupted content, and short reads.

State and persistence: no persistent state; tests use in-memory byte slices and `io.NopCloser`.

Dependencies and integration: uses JuiceFS `utils.RandRead`, Go `hash/crc32`, and standard `testing`. It indirectly verifies the shared `bufPool` path only for non-`bytes.Reader` inputs to the extent reads happen through the wrapper.

Risks and gaps: the tests focus on `bytes.Reader` generation and do not explicitly cover a generic `io.ReadSeeker` implementation. The corruption loop mutates `content[0]` and then reuses the mutated buffer for later short-read checks, which is acceptable for those assertions but can obscure intent. Invalid checksum string logging is not asserted.

Test signal: strong for the expected full-read checksum contract and the special `contentLength == -1` behavior.
