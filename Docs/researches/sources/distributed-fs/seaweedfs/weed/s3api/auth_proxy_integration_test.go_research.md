# sources/distributed-fs/seaweedfs/weed/s3api/auth_proxy_integration_test.go

Purpose: Full HTTP-stack integration tests for SigV4 verification through `httputil.ReverseProxy` with real AWS SDK v4 signatures.

Important APIs, types, and functions: `TestReverseProxySignatureVerification` configures a backend `httptest.Server` calling `iam.authRequest`, a real reverse proxy, and AWS SDK `v4.Signer.SignHTTP`.

Control flow and state: Each case writes temporary S3 credentials, starts backend and proxy servers, configures `s3.externalUrl` when needed, signs a client-facing URL, rewrites the request destination to the proxy while preserving signed headers and `Host`, and checks whether backend auth returns HTTP 200 or 403.

State and persistence behavior: Uses temp JSON config and in-memory credential store state per case. Network state is local `httptest` servers.

Dependencies and integration points: Integrates net/http request normalization, reverse proxy host rewriting, `X-Forwarded-Host` and `X-Forwarded-Proto`, `parseExternalUrlToHost`, `extractHostHeader`, and the SigV4 verifier.

Risks and test signals: Ensures proxy deployments verify against the client-facing host rather than backend host. It covers success with forwarded host, success with `externalUrl` even when the proxy omits forwarded host, default port stripping, and expected failure when neither forwarded host nor external URL preserve the signed authority.
