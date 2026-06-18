# sources/distributed-fs/seaweedfs/weed/s3api/cors/cors.go

Purpose: implements bucket CORS validation, request parsing, rule matching, response construction, wildcard handling, and HTTP header application.

Important APIs/types: `CORSRule`, `CORSConfiguration`, `CORSRequest`, `CORSResponse`, `ValidateConfiguration`, `ParseRequest`, `EvaluateRequest`, and `ApplyHeaders`, plus internal validation/matching helpers.

Control flow: validation rejects nil/empty configs, over 100 rules, unsupported methods, empty origins, invalid wildcard origins, and negative max age. `ParseRequest` identifies preflight OPTIONS and requested headers. `EvaluateRequest` selects the first origin-matching rule; preflight includes allow methods/headers only when requested method and all requested headers are allowed.

State and persistence: pure in-memory logic; struct tags define XML/JSON shape for config transport.

Dependencies and integration points: standard HTTP/string packages and middleware/storage code that supplies configs.

Risks: wildcard origin returns the caller origin rather than literal `*`. Empty allowed headers means all headers allowed. Wildcard origin matching is intentionally simple and only supports protocol-prefixed leading subdomain wildcard.
