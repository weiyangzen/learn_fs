# sources/distributed-fs/juicefs/pkg/object/checksum.go


Purpose: provides CRC32C checksum generation and read-time verification used by providers such as Tencent COS.

Important APIs and flow: `checksumAlgr` names `"Crc32c"` and `crc32c` is the Castagnoli table. `generateChecksum` consumes an `io.ReadSeeker`, using reflection to read the backing bytes of `*bytes.Reader` without copying, or streaming through `bufPool` for generic readers. It seeks back to start before returning. `verifyChecksum` and `verifyChecksum0` wrap a `ReadCloser` in `checksumReader` when a checksum string is present. `checksumReader.Read` updates CRC state and returns an error when EOF or the declared content length is reached with a mismatch.

State and persistence: no persistent state. Verification state is per-reader: expected CRC, running checksum, remaining content length, and table.

Dependencies and integration: uses shared `bufPool` from `object_storage.go` and logger for invalid checksum strings. COS stores checksums in metadata and verifies full-object reads.

Risks: reflection into `bytes.Reader` internals is brittle across Go implementation changes. Verification for content length `-1` effectively waits for EOF; partial reads before EOF do not validate. `Read` returns `0, error` on mismatch, which can discard bytes read in that call.

Test signals: `checksum_test.go` covers generation, successful validation, corrupted data, unknown length behavior, and partial-read cases.
