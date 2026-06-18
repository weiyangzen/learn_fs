# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_stream.go

Purpose: provides the memory-efficient raw chunk-copy path used when bytes can be forwarded without transformation. It replaces chunk-sized download and multipart buffers with an `io.Pipe` between source volume GET and destination volume POST.

Important APIs are `canStreamCopyChunk`, `streamCopyChunkRange`, and `shouldLogStreamError`. `canStreamCopyChunk` excludes chunks with `CipherKey` or any SSE type because those require decryption or re-encryption. Compressed chunks are eligible because full-chunk mode can forward gzip wire bytes unchanged.

Control flow in `streamCopyChunkRange` validates size, creates a cancelable child context, builds a source GET with JWT and either `Accept-Encoding: gzip` for full chunks or `Range` for partial chunks, opens an `io.Pipe`, and starts a producer goroutine that writes a multipart form part to the pipe while copying the source response body. The consumer side POSTs that multipart body to the destination volume URL with destination JWT. Errors cancel both legs and close pipe ends to avoid background draining.

State and persistence are mostly transient HTTP streams. Persistent effects occur only when the destination volume accepts the POST and stores the new file ID assigned by the caller. Source response `Content-Encoding` is treated as authoritative and copied into the multipart part only when the actual wire body is gzip.

Dependencies include `filer.JwtForVolumeServer`, `security.EncodedJwt`, global HTTP client helpers, Go `mime/multipart`, and volume server multipart upload semantics mirrored from `operation.upload_content`. Integration points are `copySingleChunk` and `copySingleChunkForRange`, which select this path for raw copy and fall back to buffered copy for transformed bytes.

Risks: the multipart framing must stay compatible with volume server parsing; the compile-time benchmark sanity uses `multipart.NewWriter` but cannot detect protocol drift. Partial ranges of compressed chunks intentionally fetch raw bytes rather than labeled gzip. Network failures must correctly unblock both goroutines, which the child context and pipe error handling address.
