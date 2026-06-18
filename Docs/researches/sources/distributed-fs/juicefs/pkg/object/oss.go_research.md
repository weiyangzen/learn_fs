# sources/distributed-fs/juicefs/pkg/object/oss.go

Purpose: implements the Alibaba Cloud OSS `ObjectStorage` backend behind the `oss` scheme when `!nooss` is enabled. It adapts the v2 Aliyun OSS SDK to JuiceFS operations: bucket creation, object head/get/put/copy/delete/list, restore, multipart upload, and pending multipart listing.

Important APIs and types: `ossClient` embeds `tierStorage` and exposes `String`, `Limits`, `Create`, `Head`, `Get`, `Put`, `Copy`, `Delete`, `List`, multipart methods, `Restore`, `autoOSSEndpoint`, and `newOSS`. `Limits` advertises OSS multipart and upload-part-copy bounds. `newOSS` parses bucket endpoints, pulls credentials from explicit args or Aliyun environment/default credential chain, determines endpoint and region, chooses signature v1/v4, configures checksums, timeouts, user agent, and shared `httpClient`.

Control flow and state: object calls are thin SDK requests with provider-specific error translation. `Head` maps 404 service errors to `os.ErrNotExist`; `Create` treats existing buckets as success; `Get`, `Put`, and `Delete` write `ResponseAttrs` request IDs and storage class when callers requested them. Full `Get` responses may be wrapped in `verifyChecksum` if checksum metadata exists. Multipart methods marshal JuiceFS `Part`/`MultipartUpload` to OSS SDK types.

Persistence and integration: data persists in one OSS bucket, with optional tier storage class and tags. Registration happens in `init` via `Register("oss", newOSS)`. It depends on shared object helpers (`obj`, `Tier`, checksum helpers, `httpClient`, `UserAgent`) and Aliyun credential providers.

Risks and test signals: region/endpoint inference is complex, especially private link and auto endpoint discovery. `ListUploads` uses `ListParts` keyed by `marker`, which may not enumerate all uploads like a true multipart-upload listing. Request-id propagation is present but not directly tested here; no OSS-specific tests in this subset.
