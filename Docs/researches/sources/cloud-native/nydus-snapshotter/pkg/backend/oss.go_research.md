# sources/cloud-native/nydus-snapshotter/pkg/backend/oss.go

Purpose: implements an Alibaba Cloud OSS backend for uploading and checking nydus blobs as objects.

Important APIs and functions: `OSSBackend` stores object prefix, OSS bucket, and force-push flag; `newOSSBackend` parses endpoint/bucket/access keys/object prefix; `splitFileByPartSize` builds multipart chunks; `push` performs one multipart upload; `Push` retries `push`; `Check`, `Type`, and `Size` implement the backend interface.

Control flow: `newOSSBackend` validates endpoint and bucket, creates an OSS client and bucket handle. `push` reads the blob descriptor from the content store, checks if the object already exists, splits it into parts by `MultipartChunkSize`, initiates multipart upload, uploads parts concurrently with `errgroup`, aborts on part failure, then completes the upload with collected parts. `Push` retries with one-, two-, four-, and eight-second backoff until success or final failure. `Size` reads `Content-Length` from object metadata.

State and persistence: remote objects are named `objectPrefix + digest.Hex()`. There is no local persistent state. Multipart uploads are explicitly aborted on part upload errors.

Dependencies and integration points: uses `github.com/aliyun/aliyun-oss-go-sdk/oss`, containerd content store, errdefs not found, and global multipart size. Converter backends can use it for remote blob storage.

Risks: uploaded parts are appended from a channel and not sorted before `CompleteMultipartUpload`; OSS SDK may require ascending part order. `Push` ignores context cancellation during `time.Sleep` and returns the last error when backoff reaches eight seconds. No test covers multipart chunking, part ordering, retry, or metadata size parsing.

Test signals: no listed tests for OSS backend.
