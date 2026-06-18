# sources/distributed-fs/ceph/src/rgw/rgw_rest_client.cc

## Purpose

`rgw_rest_client.cc` implements RGW's outbound HTTP/REST request machinery. It turns RGW request metadata, S3 object identifiers, HTTP headers, query parameters, ACLs, and bufferlists into signed HTTP requests that can be sent synchronously or through `RGWHTTPManager`. This is the low-level client used by multisite replication, remote zone forwarding, metadata forwarding, object pull/push, and helper wrappers in `rgw_rest_conn.cc`.

## Important APIs, Types, and Functions

The file defines behavior for the classes declared in `rgw_rest_client.h`: `RGWHTTPSimpleRequest`, `RGWRESTSimpleRequest`, `RGWRESTGenerateHTTPHeaders`, `RGWHTTPStreamRWRequest`, `RGWRESTStreamRWRequest`, `RGWRESTStreamS3PutObj`, and the internal `RGWRESTStreamOutCB`. The core signing helpers are `sign_request_v2()`, `sign_request_v4()`, `sign_request()`, `identify_scope()`, and `scope_from_api_name()`.

`RGWHTTPSimpleRequest` parses response headers, maps HTTP status to RGW errno with `rgw_http_error_to_errno()`, buffers bounded response data, and can stream a request body from a `bufferlist::iterator`. `RGWRESTSimpleRequest::forward_request()` rebuilds a forwarded request, signs it, applies query parameters, sends it, and returns either the remote HTTP status or a transport errno through `tl::expected<int,int>`. `RGWRESTGenerateHTTPHeaders` builds the environment and `req_info` used by RGW S3 signing code. `RGWHTTPStreamRWRequest` handles streaming request/response bodies, pause/resume, header callbacks, and embedded RGWX metadata headers.

## Control Flow

Header parsing begins in `receive_header()`: status lines update `http_status` and `status`, ordinary headers are uppercased with dash transformation and stored in `out_headers`, and an empty line calls `handle_headers()`. Simple response bodies are copied into `response` only up to `max_response`, normally learned from `CONTENT_LENGTH`.

For forwarding, `forward_request()` rebuilds `req_info`, URL-encodes the bucket component, appends this request's params, sets date and selected content headers, infers signing scope, signs with v2 or v4, appends generated headers, composes the final URL, optionally sets a request body iterator, and calls `process()`. If no HTTP status is received, it reports `-ERR_SERVICE_UNAVAILABLE`.

For streaming requests, callers must run `send_prepare()` before `send()`. `do_send_prepare()` computes path-style or virtual-host-style URL/resource layout, initializes `RGWRESTGenerateHTTPHeaders`, records an optional signing key, and attaches buffered send data. `send()` signs over the outgoing buffer when the full body is known, copies generated environment headers into the HTTP request, then queues or sends the request. `complete_request()` waits for the request, extracts `ETAG`, `RGWX_MTIME`, `RGWX_OBJECT_SIZE`, and `RGWX_ATTR_*` headers, and returns the mapped RGW status.

## State and Persistence Behavior

The file does not persist repository state directly. Runtime state lives in request objects: output headers protected by `out_headers_lock`, body buffers (`response`, `outbl`, `in_data`), signing environments (`RGWEnv` and `req_info`), stream offsets, pause flags, and optional generated headers/signing keys. These objects are short-lived per outbound HTTP operation.

The persistent effects are remote: signed requests may create or mutate objects, IAM resources, metadata, or zone state on another RGW endpoint. The code also carries object metadata across endpoints by translating RGW attrs to `x-amz-meta-*` and ACL grants to `x-amz-grant-*` headers.

## Dependencies and Integration Points

This file depends on RGW's HTTP client base, S3 auth/signing, ACL conversion, HTTP error mapping, metadata naming, Ceph bufferlists, and `req_info`/`RGWEnv`. It is consumed directly by `RGWRESTConn` and indirectly by multisite sync, IAM forwarding, remote object replication, and resource wrappers such as `RGWRESTReadResource`.

The signature path integrates with `rgw_s3_client_max_sig_ver`, AWS endpoint naming conventions, `rgw_zonegroup` fallback scope, and service-specific signing differences for S3 versus IAM. Virtual-host-style addressing rewrites both host and URL, so it must match endpoint DNS configuration.

## Risks and Edge Cases

Important risks include mismatched signing scope, especially for non-AWS endpoints, IAM forwarding, and configured `api_name`. Query parameters are encoded and merged in several places; regressions can break signatures. `RGWHTTPSimpleRequest` buffers response data rather than streaming it, so callers must set safe `max_response` values. `RGWHTTPStreamRWRequest::handle_header()` assumes `cb` is valid when `RGWX_EMBEDDED_METADATA_LEN` appears. Stream pause state and `outbl` manipulation are lock-sensitive and can deadlock if callbacks re-enter improperly.

Object paths intentionally do not encode slash characters in keys; changing that would break folder-like object names. Header case handling is also delicate: some non-`x-amz` attrs are stored in uppercase form because signing expects names such as `CONTENT_TYPE`.

## Test Signals

Useful tests include unit or integration coverage for SigV2/SigV4 generation, path-style and virtual-host-style URLs, IAM forwarding with `PayloadHash` removal, object keys containing slashes, bounded response reads, embedded RGWX metadata extraction, streaming upload pause/resume, and endpoint behavior when `process()` returns transport failure or no HTTP status.
