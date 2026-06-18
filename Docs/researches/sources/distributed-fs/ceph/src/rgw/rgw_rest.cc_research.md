# sources/distributed-fs/ceph/src/rgw/rgw_rest.cc

## Purpose

Implements common RGW REST infrastructure: HTTP status/header/body output, formatter allocation, request argument parsing, input body reading, generic object-store operation parameter handling, REST manager routing, S3 virtual-host transformation, and request preprocessing.

## Important APIs, Types, and Functions

Initialization and mappings: `rgw_rest_init()`, `rgw_to_http_attrs`, `generic_attrs_map`, status name tables, hostname sets. Response helpers: `dump_errno()`, `dump_header()`, `dump_content_length()`, `dump_etag()`, time/owner/CORS helpers, `end_header()`, `abort_early()`, `dump_continue()`, `dump_range()`, `dump_body()`. Input helpers: `recv_body()`, `rgw_rest_read_all_input()`, `read_all_chunked_input()`. Parameter helpers: `RESTArgs::*`. Operation methods cover `RGWGetObj_ObjStore`, `RGWPutObj_ObjStore`, `RGWPostObj_ObjStore`, ACL/lifecycle/object-lock/legal-hold/multipart/list/delete parameter reads. Routing classes implement `RGWRESTFlusher`, `RGWRESTOp`, `RGWHandler_REST`, `RGWRESTMgr`, and `RGWREST`.

## Control Flow and Data Flow

`RGWREST::get_handler()` preprocesses the request, resolves a manager from the decoded URI, asks it for a handler, initializes the handler, and initializes metadata info. Preprocessing stores the original URI for AWSv4 auth, attaches client IO, decodes and validates URI, resolves content length from CGI/FastCGI env variants, extracts generic metadata headers, handles `Expect: 100-continue`, and maps HTTP method to `s->op`.

Handlers use `RGWHandler_REST::get_op()` to allocate the operation for the HTTP method and initialize it. Operations use `RESTArgs` and input helpers to parse query/body state. Response flow sets request errors, sends status/headers, optionally writes formatter output, and body send/receive paths charge rate-limit byte counters.

`rgw_rest_transform_s3_vhost_style()` normalizes Host headers, matches configured S3/S3Website hostnames or CNAMEs, optionally treats the host as a bucket name, prepends the bucket to the request URI, sets website flags, and re-decodes the final URI.

## State and Persistence Behavior

This file owns process-global maps and hostname sets initialized from config and zonegroup hostnames. Per-request state is mutated heavily: `req_state` formatter, content length, generic attrs, op type, URI/domain, redirect/error headers, and rate-limit accounting. It does not persist object metadata itself, but it reads request headers into `s->generic_attrs` for later persistence by operations.

## Dependencies and Integration Points

Depends on RGW auth, op, S3/Swift REST handlers, CORS, perf counters, client IO, DNS resolver, rate limiter, formatters, UTF-8 validation, Ceph config, and SAL bucket state. It is the central integration layer between frontends, protocol handlers, RGW operations, and IO filters.

## Risks and Edge Cases

Global initialization appends to maps/sets and should be idempotent only if duplicate overwrites are harmless. Hostname suffix matching can be ambiguous; comments note missing sanity checks. Content-length compatibility chooses the larger valid length when both CGI headers exist. Chunked input reader grows chunks until max and can return partial data on `-ERANGE`. POST multipart parsing is custom and sensitive to CRLF/boundary handling. `dump_body()` and `recv_body()` charge bandwidth after transfer, not before. `abort_early()` may rewrite 404 to redirect and must avoid double formatter/header output.

## Test Signals

Cover REST init with configured extended attrs and hostnames, content-length conflict cases, zero-byte and negative lengths, zero byte in URL rejection, formatter selection from query and Accept header, all `RESTArgs` parsers, PUT max-size boundaries, POST multipart boundaries and malformed headers, chunked read limits, multipart/list parameter bounds, handler routing/default managers, S3 virtual-host/CNAME/IP/S3Website priority cases, CORS/error/redirect headers, rate-limit byte charging, and IO exception handling.
