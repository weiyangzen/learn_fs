# sources/distributed-fs/seaweedfs/weed/s3api/cors/middleware_test.go

Purpose: tests CORS middleware fallback precedence, error handling, multi-origin matching, and `Vary: Origin`.

Important fixtures/tests: `mockBucketChecker`, `mockCORSConfigGetter`, `TestMiddlewareFallbackConfig`, `TestMiddlewareFallbackConfigWithMultipleOrigins`, `TestMiddlewareFallbackWithError`, `TestMiddlewareVaryHeader`, `TestHandleOptionsRequestVaryHeader`, and `hasVaryOrigin`.

Control flow: no bucket config uses fallback; bucket config overrides fallback for both allow and deny. OPTIONS without config returns forbidden. Only `ErrNoSuchBucket` and `ErrNoSuchCORSConfiguration` trigger fallback; access denied and internal errors do not. `Vary: Origin` must be present whenever a CORS config exists, including OPTIONS.

State and persistence: in-memory mocks and mux route vars.

Dependencies and integration points: validates `Middleware.Handler`, `HandleOptionsRequest`, `getCORSConfig`, and response headers.

Risks and test signals: `Vary` can be repeated or comma-separated. `BucketChecker` is not asserted because middleware currently relies on config getter behavior.
