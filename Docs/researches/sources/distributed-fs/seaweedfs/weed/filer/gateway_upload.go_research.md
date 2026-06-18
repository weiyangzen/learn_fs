# sources/distributed-fs/seaweedfs/weed/filer/gateway_upload.go

## Purpose

`gateway_upload.go` factors shared gateway upload behavior into a reusable helper that uploads an `io.Reader` as one SeaweedFS chunk and returns the corresponding `filer_pb.FileChunk`. It is designed for NFS, WebDAV, filer gateway paths, and future gateway integrations that need common chunk assignment/upload semantics.

## Important APIs, Types, and Functions

`GatewayChunkUploader` is a small interface satisfied by `operation.Uploader`, making uploads mockable without importing the full operation package in callers. `GatewayChunkUploadRequest` carries filer client, optional uploader, reader, logical path, filename, offset, timestamp, assign-placement options, upload options, and volume-server access mode. `SaveGatewayDataAsChunk` is the main helper; `lastSlashIndex` is a local filename fallback helper.

## Control Flow

The helper rejects nil filer clients and readers, constructs a default uploader when one is not supplied, derives `Filename` from the final `FullPath` segment, creates `operation.UploadOption`, and defines a URL generator. In normal mode it emits `http://host/fileId`; in `filerProxy` mode with `FilerHTTPAddress`, it emits a proxy URL carrying `proxyChunkId`. It then builds an `AssignVolumeRequest`, calls `UploadWithRetry`, validates the returned upload result, and converts it to a protobuf file chunk using the requested offset and timestamp.

## State and Persistence Behavior

The file itself holds no persistent state. Persistence happens through the filer assignment RPC and subsequent volume-server upload performed by the uploader. The returned `FileChunk` is not installed into any filer entry here; callers must update metadata separately. This keeps the helper single-purpose and avoids hidden entry mutations.

## Dependencies and Integration Points

The code depends on `operation.NewUploader`, `operation.UploadOption`, `operation.UploadResult`, and `filer_pb.FilerClient`/`AssignVolumeRequest`. It integrates with gateway write paths that already know the logical file path and later call filer entry update APIs.

## Risks and Edge Cases

`VolumeServerAccess` only has special behavior for `filerProxy` when `FilerHTTPAddress` is non-empty; other values currently fall back to direct host URLs. A nil `UploadResult` or non-empty result error is treated as failure even if no Go error is returned. Filename derivation for trailing slashes falls back to the whole path. The helper reads through `UploadWithRetry`; short reads or content-length issues are delegated to the uploader implementation.

## Test Signals

Mock uploader tests should cover nil client/reader errors, default filename derivation, explicit filename, proxy URL generation, assign request fields, upload errors, upload-result errors, nil results, and returned chunk offset/timestamp correctness.
