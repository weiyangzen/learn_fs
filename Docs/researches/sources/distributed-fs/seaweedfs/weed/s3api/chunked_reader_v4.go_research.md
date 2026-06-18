# sources/distributed-fs/seaweedfs/weed/s3api/chunked_reader_v4.go

Purpose: implements AWS SigV4 `aws-chunked` decoding for signed streaming, unsigned streaming with trailers, checksum validation, and chunk signature chaining.

Important APIs/types: `calculateSeedSignature`, `newChunkedReader`, `extractChecksumAlgorithm`, `s3ChunkedReader`, `chunkState`, `Read`, `getChunkSignature`, CRLF/chunk-line helpers, `parseS3ChunkExtension`, `parseChunkChecksum`, `parseHexUint`, `ChecksumAlgorithm`, and `getCheckSumWriter`.

Control flow: signed streaming verifies the seed signature and stores credential, region, service, date, and seed signature. Unsigned streaming skips seed verification unless the request itself is SigV4-signed. `Read` cycles through chunk header, data read/hash, CRLF, optional signature verification, trailer checksum parsing, and EOF. Last-chunk CRLF handling accepts clients that omit an optional final CRLF.

State and persistence: per-reader state only: remaining bytes, last signature, checksum writer, chunk hash writer, trailer flag, and error.

Dependencies and integration points: IAM SigV4 helpers, `s3err`, glog, SHA/CRC hash implementations, and `crc64nvme`.

Risks: trailer signatures are not verified. `parseChunkSignature` assumes a valid marker split. Checksum errors occur after payload may have been partially streamed to callers.
