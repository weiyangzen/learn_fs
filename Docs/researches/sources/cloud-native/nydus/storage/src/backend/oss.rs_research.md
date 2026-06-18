# sources/cloud-native/nydus/storage/src/backend/oss.rs

## Purpose
This file implements the Aliyun OSS provider state and constructor on top of generic object storage. It handles OSS URL/resource construction and HMAC-SHA1 request signing.

## Important APIs, Types, and Functions
`OssState` stores access key ID/secret, scheme, object prefix, endpoint, bucket name, and retry limit. `OssState::resource` builds canonical OSS resource paths. `sign_by_url` creates a one-hour pre-signed query string. The `ObjectStorageState` implementation provides `url`, `sign`, and `retry_limit`. `pub type Oss = ObjectStorage<OssState>` exposes the backend type. `Oss::new` converts `OssConfig` to `ConnectionConfig`, constructs `Connection` and `request::Request`, initializes state, and attaches optional metrics.

## Control Flow
`url` prepends `object_prefix` to the object key, creates `scheme://bucket.endpoint/object`, and mirrors optional query strings into both the canonical resource and full URL. `sign` formats the OSS string-to-sign from method, empty MD5/content-type fields, current HTTP date, optional `x-oss-*` canonical headers, and canonical resource; it computes HMAC-SHA1, base64 encodes it, and inserts `Date` and `Authorization` headers.

## State and Persistence Behavior
`OssState` is immutable after construction and shared through `Arc` by `ObjectStorage`. Secrets are stored as plain `String`s in process memory. No blob data is cached here; persistence is in OSS and connection/proxy state.

## Dependencies and Integration Points
The module depends on `base64`, `hmac`, `sha1`, `httpdate`, `reqwest::Method`, `nydus_api::OssConfig`, and the shared connection/request/object-storage layers. It also uses the local URL encoding helper for pre-signed signatures.

## Risks
The current signing path leaves content MD5 and content type empty, which matches simple GET/HEAD but may not generalize. `object_prefix` is concatenated directly with object keys, so configuration must include any desired slash. Secrets have no redaction wrapper in `Debug` for `OssState`, although connection config logging is elsewhere. `Oss::new(None)` succeeds but later `get_reader` fails due to missing metrics.

## Test Signals
Tests cover resource and URL construction, request signing including OSS headers, constructor behavior with and without IDs, retry limit propagation, pre-signed URL creation, and preservation of path separators.
