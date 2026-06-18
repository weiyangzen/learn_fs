# sources/distributed-fs/ceph/src/rgw/rgw_common.cc

## Purpose
`rgw_common.cc` implements large shared pieces of RGW request handling and metadata behavior declared across `rgw_common.h` and related headers. It covers protocol error mapping, request initialization, metadata extraction, HTTP/query parsing, time and URL utilities, HMAC/SHA helpers, IAM/ACL permission evaluation, object lock checks, user/bucket/account JSON and binary codec support, bucket instance parsing, global initialization, and version tag generation.

## Important APIs, Types, And Functions
The global `rgw_http_*_errors` maps translate RGW/internal errno values into S3, Swift, STS, and IAM HTTP status/code pairs. `set_req_state_err()` normalizes negative errors, selects protocol-specific mappings from `req_state::prot_flags`, and falls back to S3 or `UnknownError`.

`req_info::req_info()` derives method, URI, query string, host, and parameters from `RGWEnv`, including absolute-URI normalization and stripping numeric host ports. `req_info::init_meta_info()` scans CGI-style environment headers with accepted metadata prefixes, canonicalizes them into `x_meta_map`, combines duplicates with commas, and separately tracks server-side-encryption metadata in `crypt_attribute_map`.

`RGWHTTPArgs::parse()`, `append()`, `get_bool()`, `get_int()`, and `sys_get()` parse URL query arguments, identify S3/Swift subresources and response modifiers, split system parameters with `rgwx-`, and mask password-like values in logs.

Permission flow centers on `evaluate_iam_policies()`, `verify_user_permission()`, `verify_bucket_permission()`, `verify_object_permission()`, and their no-policy ACL fallbacks. These functions account for explicit deny precedence, resource/identity/session policy interaction, account root, cross-account requests requiring separate allows, requester-pays, Block Public Access, object ownership mode, deferred bucket ACL checks, and Swift ACL enforcement.

Utility implementations include RFC2616/ISO8601 parsing, URL encode/decode, whitespace/quote trimming, HMAC-SHA1/SHA256, streaming SHA256 helpers, wildcard policy matching by colon-delimited components, cap/op parsing, and pool/object string conversions.

Codec and dump implementations include `RGWBucketInfo`, `RGWUserInfo`, `RGWAccountInfo`, `RGWGroupInfo`, `RGWBucketEnt`, `RGWStorageStats`, `RGWSubUser`, `RGWAccessKey`, `rgw_obj_key`, `rgw_raw_obj`, and related test-instance generators.

## Control Flow
A typical request starts with `req_state` construction, which embeds `req_info`, copies logging flags and ACL deferral config from `RGWEnv`, and records a coarse start time for log prefixes. Handlers parse query args and metadata, authenticate identity elsewhere, then call verification helpers. Permission helpers first evaluate IAM policy effects, short-circuit explicit denies/allows, and fall back to ACL checks only when policy did not decide and policy is not mandatory. Error paths call `set_req_state_err()` and `dump()` to render protocol-specific error objects.

Bucket and user metadata flows call binary `encode()`/`decode()` methods declared inline in `rgw_common.h` plus JSON dump/decode functions here. `RGWBucketInfo::decode()` contains substantial compatibility logic across layout versions, owner encoding changes, website/versioning/object-lock/sync-policy additions, and synthesized log layout defaults.

## State And Persistence Behavior
This file manipulates persistent metadata structures but does not itself perform RADOS IO. Encoded structs are persisted by other layers as bucket/user/account metadata objects or attrs. Compatibility is critical: `RGWBucketInfo::encode()` writes version 24 with owner duplicated in old user fields, while `decode()` supports legacy versions and reconstructs new layouts. `RGWUserInfo` encodes version 23 with account, path, create date, tags, and group ids while maintaining older access-key fields. `RGWObjVersionTracker::generate_new_write_ver()` creates a new random tag and version sequence used by RADOS versioned writes in other files.

## Dependencies And Integration Points
The implementation depends on Ceph JSON/Formatter, crypto wrappers, global init, OpenSSL setup, IAM policy classes, ACLs, object lock, bucket layout/sync policy, SAL bucket/object interfaces, and `rgw_http_errors.h`. It is central infrastructure used by almost every RGW REST operation and admin path.

## Risks And Edge Cases
Permission ordering is high risk: explicit deny, cross-account policy intersection, session policy behavior, requester-pays, public access block, and object-ownership ACL suppression must match S3 semantics. Query parsing uses string indexing such as `name[0]` after parsing; empty query names should be considered in tests. `url_decode()` returns an empty string on malformed hex, which is ambiguous with a valid empty result. `rgw_string_unquote()` indexes `s[0]` before checking size, so empty input would be unsafe if callers pass it. Legacy decode paths and duplicated owner fields are compatibility-sensitive. `RGWCompletionInfo` is not here, but compression attrs and object lock attrs consumed elsewhere rely on constants from the header.

## Test Signals
Test signals include encode/decode round trips from `generate_test_instances()`, dbstore tests using `RGWUserInfo` and `RGWBucketInfo`, protocol error mapping tests for S3/Swift/IAM/STS flags, permission matrix tests for IAM/ACL/session/cross-account/public-access/requester-pays/object-ownership, URL and query parser fuzz cases, and bucket instance parse cases with and without shard ids.
