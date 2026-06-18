# sources/distributed-fs/juicefs/pkg/object/dragonfly.go


Purpose: implements a Dragonfly object-storage gateway backend behind `!nodragonfly`, registering `dragonfly`.

Important APIs and flow: `dragonfly` talks HTTP to dfdaemon object-storage endpoints. `Create` posts `/buckets/{bucket}` after probing list. `Head`, `Get`, `Put`, `Copy`, `Delete`, and `List` build REST requests under `/buckets/{bucket}`. `Put` and `Copy` use multipart form bodies; write mode can be synchronous `WriteBack` or `AsyncWriteBack`. `List` decodes JSON `ObjectMetadatas`, merges common prefixes, and caps page size at `MaxGetObjectMetadatasLimit`.

State and persistence: object data may be written to Dragonfly cache and backend storage depending on mode. Local state includes endpoint, bucket, selected query filter, write mode, max replicas, and HTTP client.

Dependencies and integration: uses shared `getRange`, `generateListResult`, `obj`, `httpClient`, and `ResponseAttrs`. `newDragonfly` calls `/metadata` to identify the underlying object store and chooses URL-query filters for S3, OSS, or OBS presigned URLs.

Risks: some methods use `http.DefaultClient` rather than `d.client`, reducing consistency. Bucket parsing keeps `uri.Path`, which may include a leading slash in the bucket field. `Delete` treats non-2xx, including not found, as an error. `Put` buffers the complete multipart payload in memory. `getObjectStorageMetadata` returns `nil, nil` on URL parse failure, which can hide errors.

Test signals: environment-gated `TestDragonfly` runs the shared object-storage suite with a configured endpoint.
