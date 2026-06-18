# sources/distributed-fs/ceph/src/rgw/rgw_auth_s3.cc

## Purpose

`sources/distributed-fs/ceph/src/rgw/rgw_auth_s3.cc` implements S3 signature canonicalization, AWS Signature Version 2 and Version 4 parsing/signing helpers, streaming AWSv4 payload completers, trailer signature validation, canonical method selection, and auth-type logging helpers. The source was read as a complete 1782-line implementation.

## Important APIs, Types, and Functions

Top-level helpers include `rgw_create_s3_canonical_header()` overloads, `get_canon_resource()`, `get_canon_amz_hdrs()`, and `get_v2_qs_map()`. In `rgw::auth::s3`, important functions include `is_time_skew_ok()`, `parse_v4_credentials()`, `gen_v4_scope()`, `get_v4_canonical_qs()`, `gen_v4_canonical_qs()`, `get_v4_canonical_headers()` overloads, `get_v4_canon_req_hash()`, `get_v4_string_to_sign()`, `get_v4_signature()`, `get_v2_signature()`, `get_canonical_method()`, and `get_aws_version_and_auth_type()`. Completer logic lives in `AWSv4ComplMulti::ChunkMeta`, `AWSv4ComplMulti`, and `AWSv4ComplSingle`.

## Control Flow

Signature v2 canonicalization validates Content-MD5 base64 characters, chooses Date/Expires behavior for header vs query auth, parses request time, gathers x-amz metadata/query security token fields, orders signed subresources, and emits the string to sign. Signature v4 parsing handles query-string presign fields or Authorization header key/value fields, validates dates/time skew, splits credential scope, extracts access key id, builds canonical query strings and headers, hashes canonical requests, builds strings to sign, derives signing keys, and computes server signatures.

For streaming AWSv4, `AWSv4ComplMulti` installs itself as an IO filter, parses chunk metadata, verifies each previous chunk signature after the next chunk boundary is known, streams payload bytes while updating SHA256, adjusts decoded content length, consumes final zero-length chunk/trailer bytes, optionally extracts declared trailing headers into request properties, and validates trailer signatures when expected. `AWSv4ComplSingle` filters non-chunked signed bodies and validates the final payload hash in `complete()`.

## State and Persistence Behavior

The file does not persist state externally. It mutates request state by installing auth filters, updating decoded content length, adding trailer-derived properties, and populating auth logging strings. Completers keep in-memory stream position, current chunk metadata, previous chunk signature, signing key, SHA256 contexts, parsing buffers, and trailer expectations for the lifetime of a request body.

## Dependencies and Integration Points

Dependencies include RGW REST/S3 request structures, HTTP environment maps, `rgw_client_io`, Ceph crypto/HMAC/SHA helpers, UTF-8 encoding, URL recoding, query parsing, CORS method validation, sanitized logging, and AWS auth abstractor types declared in `rgw_auth_s3.h`. The output feeds S3/Keystone AWS engines by producing string-to-sign values, signature factories, and completer factories.

## Risks and Edge Cases

Canonicalization is compatibility-sensitive: query parameter ordering, slash encoding, host port handling for Boto2 presigned URLs, signed subresource lists, whitespace trimming, and non-S3 operation parameter filtering can change auth outcomes. Presigned v4 expiration is capped at seven days and maps expiration to special errors. Chunk parsing uses fixed metadata and trailer buffer limits, supports signed and unsigned chunked modes, and must correctly handle boundary variants with optional leading CRLF. Missing signed headers are tolerated by skipping unavailable env vars, which can affect compatibility/security expectations. Secrets and strings-to-sign are logged only through sanitizing paths in some but not all diagnostic branches.

## Test Signals

Tests should cover SigV2 canonical strings for headers/query/subresources, invalid Content-MD5 rejection, SigV4 header and query parsing errors, time skew and presigned expiration, canonical query sorting and plus-to-space handling, canonical header trimming and host-port Boto2 compatibility, non-S3 operation canonical method/query behavior, signing-key derivation, v2/v4 signature matches against AWS examples, single-payload hash completion, signed chunked streaming with trailers, unsigned chunked streaming, final chunk/trailer signature mismatch, trailer buffer limit, and CORS OPTIONS canonical method validation.
