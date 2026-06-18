# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_checksum_test.go

Purpose: unit-tests UploadPartCopy checksum propagation and XML response fields. It ensures multipart upload checksum configuration stored on the upload entry is replayed onto the fake put request and that copy-part responses expose the correct checksum element.

Important coverage includes `TestApplyDestChecksumHeaderToCopyRequest`, `TestUploadEntryHasChecksum`, and `TestBuildCopyPartResult`. These target `applyDestChecksumHeaderToCopyRequest`, `uploadEntryHasChecksum`, checksum algorithm detection, and `buildCopyPartResult`.

Control flow creates filer entries with `ExtChecksumAlgorithm`, applies checksum headers to synthetic PUT requests, then verifies `detectRequestedChecksumAlgorithm` sees the intended algorithm and header. It also checks nil entries, empty entries, and unknown algorithms do not produce false positives. The XML response test iterates over CRC32, CRC32C, CRC64NVME, SHA1, SHA256, and unknown headers, comparing struct fields and encoded XML snippets.

State and persistence are pure in-memory request headers and `filer_pb.Entry.Extended` metadata. No network, filer, or volume server is involved.

Dependencies include `s3_constants`, `s3err.EncodeXMLResponse`, checksum helper functions defined elsewhere in the package, and `SSEResponseMetadata`. Integration point is the slow UploadPartCopy path in `copyObjectPartViaReencryption`, where checksum headers are staged before calling `putToFiler`.

Risks: these tests validate header translation and response shape but not end-to-end checksum computation on uploaded bytes. They are still important because missing checksum staging causes multipart complete failures for checksum-enabled uploads copied through UploadPartCopy.
