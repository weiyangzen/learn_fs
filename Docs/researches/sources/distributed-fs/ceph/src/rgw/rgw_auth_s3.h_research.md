# sources/distributed-fs/ceph/src/rgw/rgw_auth_s3.h

Purpose: declares S3 authentication strategy composition plus SigV2/SigV4 canonicalization and streaming payload completion helpers for RGW. It is the public interface between REST S3 request handling, auth engines, and body readers that must verify SigV4 payload integrity.

Important APIs/types/functions: `STSAuthStrategy`, `ExternalAuthStrategy`, and templated `AWSAuthStrategy<AbstractorT, AllowAnonAccessT>` assemble auth engines and `IdentityApplier` factories. `AWSv4ComplMulti` and `AWSv4ComplSingle` implement `rgw::auth::Completer` and decorate `rgw::io::RestfulClient` body reads. Helpers include `rgw_create_s3_canonical_header()`, `parse_v4_credentials()`, `gen_v4_scope()`, URI encoding/recode helpers, payload-hash classifiers, canonical query/header builders, `get_v4_canon_req_hash()`, `get_v4_string_to_sign()`, `get_v4_signature()`, `get_v2_signature()`, and `get_aws_version_and_auth_type()`.

Control flow: `AWSAuthStrategy` optionally installs anonymous auth, parses `rgw_s3_auth_order`, filters configured STS/external/local engines, and adds the last engine as `FALLBACK` when multiple engines exist. `AWSv4ComplMulti` tracks chunk metadata, stream position, previous chunk signature, optional trailers, and SHA256 state as body bytes are received. `AWSv4ComplSingle` streams a body hash and compares it against the expected `x-amz-content-sha256` value in `complete()`.

State/persistence: no durable state is written here, but request state is modified by completers; `AWSv4ComplMulti::put_prop()` mutates the CGI/env map to surface validated trailer headers. The auth strategies retain pointers/references to `CephContext`, SAL driver, implicit tenant context, and auth engines.

Dependencies/integration: depends on `rgw_auth`, `rgw_auth_filters`, Keystone/LDAP auth, `rgw_rest_s3`, request env maps, Ceph crypto SHA256, and S3 canonicalization utilities. REST S3 operations call these declarations through auth engines and completers.

Risks: signature correctness is sensitive to URI recoding, plus-to-space behavior, missing `x-amz-content-sha256`, auth engine ordering, and chunk/trailer boundary parsing. `parse_auth_order()` silently falls back to default on unknown names. Streaming unsigned/trailer variants must stay aligned with AWS semantics.

Test signals: cover SigV2/SigV4 canonical strings, presigned URLs, reordered auth engine config, STS/external/local fallback, empty/unsigned/streaming/trailer payload modes, chunk signature mismatch, malformed chunk metadata, and trailer checksum propagation.
