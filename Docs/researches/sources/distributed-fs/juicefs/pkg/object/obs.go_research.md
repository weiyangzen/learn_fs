# sources/distributed-fs/juicefs/pkg/object/obs.go


Purpose: implements Huawei Cloud OBS behind `!noobs`, registering `obs`.

Important APIs and flow: `obsClient` wraps the OBS SDK and tier config. It supports create, limits, head, get, put, copy, restore, delete, list, multipart create/upload/copy/abort/complete/list. `Put` computes MD5 and content length for all inputs, sets content MD5, MIME type, storage class, and optional tags, then optionally validates ETag when bucket encryption is absent. `Copy` can replace tags by adding placeholder metadata. `newOBS` normalizes endpoint, discovers bucket region when needed, configures proxy from environment, disables SDK retry due to seek issues, and detects whether ETag checking is safe.

State and persistence: object data, storage class, tags, restore status, and multipart uploads persist in OBS. Local state includes bucket, region, ETag-check flag, SDK client, and tiers.

Dependencies and integration: uses Huawei OBS SDK, shared `Tier`, `ResponseAttrs`, `getRange`, `checkGetStatus`, and `httpClient` transport.

Risks: non-seekable puts buffer entire data. Region parsing assumes known OBS hostname format. ETag validation is disabled for encrypted buckets but detection can warn and continue. SDK retry is disabled, affecting transient-failure resilience. `ListAll` unsupported.

Test signals: `TestOBS` is environment-gated and runs the shared storage suite.
