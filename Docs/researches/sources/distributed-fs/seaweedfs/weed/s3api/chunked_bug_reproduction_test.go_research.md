# sources/distributed-fs/seaweedfs/weed/s3api/chunked_bug_reproduction_test.go

Purpose: narrow regression reproduction for GitHub issue #6847, where clients send unsigned streaming headers with signed-looking chunk extensions.

Important APIs: `TestChunkedEncodingMixedFormat`, `setupTestIAM`, and `IdentityAccessManagement.newChunkedReader`.

Control flow: the request advertises `STREAMING-UNSIGNED-PAYLOAD-TRAILER` and a CRC32 trailer while the body chunks contain `;chunk-signature=` values. The reader must decode framing, skip signature verification without credentials, validate the trailer checksum, and return only payload bytes.

State and persistence: no persistent state; IAM is intentionally empty to hit the nil-credential mixed-format path.

Dependencies and integration points: chunked reader state machine, S3 error codes, and checksum trailer parsing.

Risks and test signals: guards against nil pointer dereference and over-strict parsing for newer AWS SDK behavior. Broader signed/invalid cases live in the main chunked reader tests.
