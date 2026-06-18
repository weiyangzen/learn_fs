# sources/cloud-native/soci-snapshotter/service/resolver/client.go

Purpose: HTTP client and authentication support for registry/blob resolver operations. It configures retryable HTTP behavior, Docker auth integration, sensitive URL redaction, token-expiration workarounds, and auth context propagation.

Important APIs/types/functions: `globalHeaders` sets the SOCI User-Agent. `newAuthClient` builds a `socihttp.AuthClient` around containerd `docker.Authorizer`. `newRetryableClientFromConfig` applies retry counts, waits, backoff, retry strategy, error handler, and timeouts. `CloneRetryableClient`, `jitter`, `backoffStrategy`, `retryStrategy`, and `handleHTTPError` define retry behavior. `dockerAuthHandler` implements `AuthHandler`. `shouldAuthenticate` handles 401, ECR expired-token 403, and S3 expired-token 400 XML. `newContextWithScope` carries Docker token scopes into replay contexts.

Control flow: resolver creates a retryable client, wraps it in AuthClient, sends requests through authorization/retry layers, retries transient errors with jittered backoff, redacts query values on logging/final errors, and reauthenticates on selected responses. ECR expired 403 bodies are parsed as Docker errors and may synthesize a `Www-Authenticate` header; S3 expired-token XML normalizes status to 401 but returns false so upstream blob fetch logic can refresh pre-signed URLs.

State and persistence: no global mutable state except `userAgent` string. Retryable clients carry configuration and HTTP transport timeouts. Auth state is delegated to containerd Docker authorizer and credential callbacks.

Dependencies/integration points: integrates `internal/http.AuthClient`, containerd remotes/docker authorizer, retryablehttp, project config, version, logrus/containerd logging, and XML/JSON registry error formats.

Risks: `CloneRetryableClient` intentionally does not clone HTTP timeout/transport settings, only retry policies. `shouldAuthenticate` reads and restores response bodies; nil bodies would panic if passed for 403/400 paths. ECR workaround hardcodes message/service. S3 branch returns false after mutating status, relying on caller behavior outside this function.

Test signals: `client_test.go` covers redacted final errors, response body drain/close, 401 auth, ECR expired-token 403 auth/header synthesis, and ordinary 403/200 no-auth cases.
