# sources/distributed-fs/ceph/src/rgw/rgw_loadgen.cc

Purpose: Implements a synthetic client IO and request environment for RGW load generation. It signs generated S3 requests and feeds them into RGW processing without real network IO.

Important APIs and functions: `RGWLoadGenRequestEnv::set_date()` formats the request date. `RGWLoadGenRequestEnv::sign()` builds an S3 v2 canonical header and authorization header. `RGWLoadGenIO::init_env()` populates `RGWEnv` from the generated request. `read_data()`, `write_data()`, status/header methods, `flush()`, and `complete_request()` implement no-op or byte-counting IO behavior.

Control flow: A generated request sets method, URI, content type/length, date, and headers. `sign()` uses the configured access key to add `HTTP_DATE` and `HTTP_AUTHORIZATION`. `RGWLoadGenIO` then exposes this data through `RGWEnv` and simulates request body reads by decrementing `left_to_read`; response writes and headers are discarded.

State and persistence: The request environment is per request. `left_to_read` tracks remaining synthetic body bytes. No response data is persisted and no actual network traffic is emitted. Storage mutations occur later when the request is processed by RGW.

Dependencies and integration points: Depends on `rgw_auth_s3` for canonicalization/signing, global Ceph context for S3 signature helper, and RGW client IO abstractions. It is used by `RGWLoadGenProcess` in `rgw_loadgen_process.cc`.

Risks: This is not a full HTTP client and intentionally ignores response bodies/headers, so it is suitable for load generation rather than protocol validation. It uses S3 v2 signing and a global context dependency. `read_data()` does not fill the buffer with deterministic payload bytes, which may matter for checksum-sensitive paths.

Test signals: Tests should cover canonical header inputs, authorization header format, env variable population, body length simulation, zero-length bodies, and operation paths that require response handling or request body content.
