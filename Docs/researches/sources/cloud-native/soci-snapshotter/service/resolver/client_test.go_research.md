# sources/cloud-native/soci-snapshotter/service/resolver/client_test.go

Purpose: unit tests for resolver HTTP error redaction, body draining, and authentication policy decisions.

Important APIs/types/functions: `TestHandleHTTPErrorRedactsHTTPQueries`, `TestHandleHTTPErrorReadsAndClosesResponseBody`, `mockBody`, and `TestAuthentication`. Constants define S3-like URL/query expectations.

Control flow: error tests create responses with sensitive query parameters and/or `url.Error`, call `handleHTTPError`, and compare final error strings. Body test verifies `handleHTTPError` reads and closes response body. Auth tests build Docker error JSON bodies for ECR expired token, normal forbidden, unauthorized, and OK, then assert `shouldAuthenticate` result and synthesized header where expected.

State and persistence: in-memory fake response bodies track read/close flags.

Dependencies/integration points: uses containerd Docker error types, Go URL/HTTP primitives, and resolver constants for ECR token expiration.

Risks: string comparisons are exact and can be brittle if error wording changes. Auth tests do not cover S3 XML expired-token branch. The test loop in `TestAuthentication` does not call `t.Run`, so a failure identifies the case through message only.

Test signals: confirms sensitive query redaction in final errors, response body cleanup on retry exhaustion, and major auth policy branches for Docker/ECR responses.
