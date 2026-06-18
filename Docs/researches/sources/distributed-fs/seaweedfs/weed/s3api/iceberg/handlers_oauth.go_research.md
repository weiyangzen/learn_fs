# Research: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/handlers_oauth.go

## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/handlers_oauth.go

Purpose: OAuth2 client-credentials support for the Iceberg REST catalog. It lets S3 access-key credentials obtain bearer JWTs and lets catalog routes authenticate those bearer tokens.

Important APIs: `OAuthTokenResponse`, `OAuthErrorResponse`, and `IcebergClaims` define wire/token shapes. `handleOAuthTokens` parses form or HTTP Basic credentials, rejects `client_secret` in the URL, requires `grant_type=client_credentials`, validates credentials through `CredentialValidator`, signs an HS256 JWT using `deriveSigningKey(accessKey, secret)`, and returns a one-hour bearer token. `authenticateBearer` extracts the bearer token, parses claims without validation to find the access key, fetches the current credential secret, verifies signature and expiry, and returns identity info. `writeOAuthError` emits OAuth-shaped JSON errors.

State and dependencies: no server-side token store is used; token validity depends on current credential lookup. Dependencies include `golang-jwt/jwt/v5`, HMAC-SHA256, the server credential validator, and shared `writeJSON`. Integration points are `Server.Auth` and `/v1/oauth/tokens`. Risks: unverified parsing is deliberately used only to choose a verification key; credential rotation invalidates old tokens; the token is signed from the client secret, so validator availability is required for both issuance and verification. Tests cover success, invalid credentials, unsupported grant type, and bearer round trips.
