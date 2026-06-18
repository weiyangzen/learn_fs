# sources/distributed-fs/seaweedfs/weed/s3api/cors/middleware.go

Purpose: HTTP middleware that applies bucket or fallback CORS policy to S3 API requests and short-circuits preflights.

Important APIs/types: `BucketChecker`, `CORSConfigGetter`, `Middleware`, `NewMiddleware`, `getCORSConfig`, `Handler`, `HandleOptionsRequest`, and `processCORS`.

Control flow: request bucket is extracted from S3 route constants. Config lookup prefers bucket CORS, then fallback only for no config or no-such-bucket cases; other errors stop fallback. If config exists, `Vary: Origin` is added. Non-CORS requests continue. Preflight without config or failed evaluation returns access denied. Successful preflight writes CORS headers and 200; successful actual requests apply headers then call next.

State and persistence: holds provider references and optional fallback config; no persistence.

Dependencies and integration points: integrates `cors.go`, `s3_constants.GetBucketAndObject`, S3 error response writing, and glog.

Risks: `BucketChecker` is injected but unused in current flow. Fallback for `ErrNoSuchBucket` intentionally prevents CORS-based bucket-existence disclosure but can decorate 404 responses.
