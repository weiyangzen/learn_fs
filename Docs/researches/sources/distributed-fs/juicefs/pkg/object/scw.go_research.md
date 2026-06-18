# sources/distributed-fs/juicefs/pkg/object/scw.go

Purpose: implements Scaleway Object Storage support as a thin S3-compatible wrapper registered as `scw`.

Important APIs and types: `scw` embeds `s3client`, overrides `String`, and customizes `Limits` to set `MaxPartCount` to 1000 while retaining S3 multipart and upload-part-copy support. `newScw` parses endpoint, bucket, and region, and builds an AWS S3 client with Scaleway endpoint settings.

Control flow and state: endpoint defaults to HTTPS when no scheme is present. The bucket is the first hostname segment; region is read from the third segment; base endpoint is the host without the bucket prefix. Credentials may come from args or `SCW_ACCESS_KEY`/`SCW_SECRET_KEY`. The client uses unsigned payload middleware, shared HTTP client, path-style disabled, and one retry attempt.

Persistence and integration: actual behavior is inherited from `s3client`, so storage class, request attributes, listing, and multipart behavior follow the S3 adapter unless limited by Scaleway.

Risks and test signals: host parsing assumes Scaleway's endpoint layout and may panic or misparse malformed hosts. No SCW-specific tests are present; coverage depends on generic S3 behavior.
