# sources/distributed-fs/seaweedfs/weed/s3api/auth_signature_v4_test.go

Purpose: Unit tests for SigV4 parsing, payload hashing, forwarded-prefix joining, host extraction, and signed header canonicalization.

Important APIs, types, and functions: Exercises `extractV4AuthInfoFromHeader`, `parseSignedHeader`, `extractV4AuthInfoFromQuery`, `buildPathWithForwardedPrefix`, `extractHostHeader`, `extractSignedHeaders`, and `getCanonicalHeaders`.

Control flow and state: Tests compare S3 vs non-S3 services for auto body hashing; reject empty signed-header names in Authorization and presigned query paths; verify forwarded prefix joining preserves double slashes and trailing slash S3 key semantics; and run a large table of host extraction cases across forwarded host/port/proto, external host override, IPv6, default ports, and misaligned proxy ports.

State and persistence behavior: No persistent state. Request bodies are in-memory readers; host extraction uses mock requests.

Dependencies and integration points: Tightly coupled to AWS SDK host sanitization expectations used by `auth_security_test.go` and `auth_proxy_integration_test.go`.

Risks and test signals: These tests protect compatibility with S3 clients behind proxies and prevent malformed signed-header lists from silently changing canonical requests. They do not independently verify full signatures except through sibling integration/security tests.
