# sources/distributed-fs/seaweedfs/weed/s3api/chunked_reader_v4_test.go

Purpose: tests SigV4 chunked reader behavior for unsigned trailer uploads, signed chunk chains, checksum trailers, invalid signatures, and service-scope handling.

Important helpers/tests: `setupIam`, `NewRequestStreamingUnsignedPayloadTrailer`, `generateStreamingUnsignedPayloadTrailerPayload`, `TestNewSignV4ChunkedReaderStreamingUnsignedPayloadTrailer`, `TestSignedStreamingUpload`, `createTrailerStreamingRequest`, `TestSignedStreamingUploadWithTrailer`, `TestSignedStreamingUploadWithTrailerInvalidSignature`, and `TestSignedStreamingUploadInvalidSignature`.

Control flow: unsigned trailer payloads use CRC32 and both final-CRLF variants. Signed tests compute seed, chunk, and final signatures dynamically and require decoded concatenated data. Invalid chunk signatures must fail during read. Invalid trailer signatures currently may still allow content unless future validation is added.

State and persistence: in-memory IAM credentials and synthetic request bodies.

Dependencies and integration points: SigV4 helpers, checksum writers, default test credentials, `s3err`, and testify assertions.

Risks and test signals: confirms case-insensitive checksum algorithm extraction and dynamic signed chunk validation. Documents the current trailer signature validation gap.
