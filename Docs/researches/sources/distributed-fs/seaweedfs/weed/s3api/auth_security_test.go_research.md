# sources/distributed-fs/seaweedfs/weed/s3api/auth_security_test.go

Purpose: Security regression tests for S3 authentication enforcement, signature-only paths, internal header spoofing, anonymous unsigned streaming uploads, and proxy/external URL signature behavior.

Important APIs, types, and functions: `signRawHTTPRequest` signs requests with the real AWS SDK. `TestReproIssue7912` exercises `NewIdentityAccessManagementWithStore`, `authRequest`, `AuthSignatureOnly`, `isAdmin`, and `CanDo`. `TestAnonymousStreamingUnsignedUpload` covers anonymous unsigned-streaming auth. `TestExternalUrlSignatureVerification` and `TestRealSDKSignerWithForwardedHeaders` validate host canonicalization against real SDK signatures.

Control flow and state: The issue reproduction loads a config with admin/read-only users and asserts unknown keys, wrong secrets, anonymous protected requests, and arbitrary credentials are denied while valid credentials pass. It also checks `AuthSignatureOnly` accepts valid signatures, rejects bad signatures and unsigned-streaming without auth, and strips client-supplied SeaweedFS principal/session headers. The anonymous streaming test loads only an anonymous identity and expects a checksum-trailer PUT without Authorization to authenticate as anonymous. Proxy tests sign against external/client hosts and verify SeaweedFS extracts matching hosts.

State and persistence behavior: Tests use temporary config files, memory credential store reset around tests that can leak anonymous state, and per-test IAM managers.

Dependencies and integration points: Depends on AWS SDK v2 signing, `httptest`, S3 constants/errors, and the v4 host/signature code. It cross-checks behavior across `auth_credentials.go`, `auth_signature_v4.go`, and auth-type detection/chunked upload support.

Risks and test signals: Protects against auth bypasses and privilege escalation: unknown credentials must not be accepted, internal IAM headers must not be client-spoofable, unsigned streaming must not bypass auth, and reverse-proxy host handling must match AWS SDK canonicalization.
