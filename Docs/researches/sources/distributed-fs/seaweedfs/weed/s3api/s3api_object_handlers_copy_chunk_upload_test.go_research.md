# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_chunk_upload_test.go

Purpose: protects chunk-copy upload memory behavior and concurrency safety. It verifies `newChunkUploadOption` always supplies a private pre-sized `BytesBuffer`, bypassing the package-global bytebufferpool that previously retained large multipart buffers under UploadPartCopy load.

Important APIs covered are `TestNewChunkUploadOption_AvoidsBytePool` and `TestNewChunkUploadOption_PerCallIsolation`. They exercise `newChunkUploadOption`, `multipartFramingOverhead`, `UploadOption.BytesBuffer`, `UploadOption.Cipher`, and destination URL/JWT setup through an `AssignVolumeResponse`.

Control flow iterates over empty, small, 8 MiB, and 64 MiB chunks. For each, it builds an upload option and asserts that `BytesBuffer` is non-nil, has at least `len(chunkData)+multipartFramingOverhead` capacity, starts empty, and has `Cipher=false` because chunk-copy bytes are already encrypted when the source had a cipher key. The isolation test calls the helper twice and asserts distinct buffers, preventing accidental sharing across concurrent uploads.

State and persistence are limited to allocated buffers and upload option structs. No HTTP upload is performed.

Dependencies include `filer_pb.AssignVolumeResponse` and `operation.UploadOption` returned by the implementation. Integration point is `uploadChunkData`, which passes this option into `operation.NewUploader().UploadData`.

Risks: this test does not validate multipart wire format or upload success; the benchmark file and stream-copy code cover that separately. Its core signal is preventing a regression to global pooled buffers and preventing shared mutable buffer state in concurrent copy operations.
