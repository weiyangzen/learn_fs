# sources/distributed-fs/seaweedfs/weed/s3api/custom_types.go

Purpose: defines small shared S3 API constants/types.

Important API/type: `s3TimeFormat` and `ConditionalHeaderResult`.

Control flow: no functions. `ConditionalHeaderResult` carries an S3 error code, an ETag for 304 responses, and an optional fetched filer entry from conditional header checks.

State and persistence: no persistence. The `Entry` pointer may be nil because no fetch happened or because the object did not exist, depending on caller context.

Dependencies and integration points: imports `filer_pb.Entry` and `s3err.ErrorCode`; used by conditional request handling elsewhere in S3 API.

Risks: downstream users must not overinterpret nil `Entry`. Changing `s3TimeFormat` can affect wire timestamp compatibility.
