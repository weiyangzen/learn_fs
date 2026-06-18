# sources/distributed-fs/juicefs/pkg/object/ks3.go


Purpose: implements Kingsoft KS3 storage behind `!nos3 && !noks3`, registering `ks3`.

Important APIs and flow: `ks3` wraps the KS3 SDK. It implements create, limits, head, get, put, copy, delete, list, restore, multipart create/upload/copy/abort/complete/list. Helper dereference functions handle nullable time and bool pointers. `Head` maps 404 to `os.ErrNotExist` and defaults storage class to `STANDARD` when metadata is absent. `Put` buffers non-seekable readers, guesses MIME type, applies tier storage class and tag. `newKS3` parses bucket and region from endpoint host, maps KS3 regions, optionally uses AWS_REGION for non-KS3 endpoints, and unescapes credentials.

State and persistence: object data, metadata, tags, restore status, and multipart uploads persist in KS3. Local state is bucket, SDK client, and tiers.

Dependencies and integration: uses `github.com/ks3sdklib/aws-sdk-go`, shared `decodeKey`, `DefaultStorageClass`, `ResponseAttrs`, and package `httpClient`.

Risks: endpoint parsing assumes bucket.region host patterns and slices `hostParts[1][3:]`. For native KS3 domains, path-style is disabled. Non-seekable puts are fully buffered. List upload timestamp parsing has a FIXME. Request/storage-class attrs depend on KS3 metadata keys.

Test signals: `TestKS3` is environment-gated on `KS3_ACCESS_KEY` and runs the shared object-storage contract.
