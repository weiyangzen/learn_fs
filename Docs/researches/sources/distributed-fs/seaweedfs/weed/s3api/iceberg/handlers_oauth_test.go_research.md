# Research: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/handlers_oauth_test.go

## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/handlers_oauth_test.go

Purpose: unit tests for Iceberg OAuth token issuance and bearer authentication.

Important components: `mockCredentialValidator` implements both `ValidateS3Credential` and `GetCredentialByAccessKey` over in-memory access-key maps. `newTestServerWithOAuth` builds a server with one credential. `TestHandleOAuthTokens_Success` posts `client_credentials` form data and verifies status, token type, non-empty access token, and expiry. `TestHandleOAuthTokens_InvalidCredentials` expects 401. `TestHandleOAuthTokens_UnsupportedGrantType` expects 400. `TestBearerTokenRoundTrip` obtains a token then authenticates a bearer request and checks the identity name. `TestBearerTokenInvalid` and `TestBearerTokenNone` reject bad/missing tokens.

State and dependencies: all state is local to the mock validator and httptest recorder/request. Dependencies are JSON, net/http, httptest, strings, and the OAuth handler under test. Integration point is `Server.Auth`, which calls `authenticateBearer` before falling back to S3 request authentication. Risks not covered include Basic auth input, URL secret rejection, expired tokens, wrong signing methods, and credential rotation, but the core issuance/verification path has direct coverage.
