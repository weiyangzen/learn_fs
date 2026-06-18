# Research: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/server.go

## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/server.go

Purpose: server wiring for the Iceberg REST Catalog API: dependencies, route registration, logging middleware, and authentication middleware.

Important APIs: `FilerClient`, `S3Authenticator`, and `CredentialValidator` interfaces decouple the catalog from concrete S3/filer/IAM implementations. `Server` stores filer access, S3 Tables manager, authenticator, OAuth credential validator, and advertised S3 endpoint. `NewServer` constructs a manager and mirrors default-allow from the S3 authenticator. `SetCredentialValidator` and `SetS3Endpoint` configure optional OAuth/FileIO behavior. `RegisterRoutes` installs logging and path validation middleware, public config/OAuth endpoints, authenticated namespace/table endpoints with and without `/v1/{prefix}`, and a JSON catch-all. `Auth` prefers bearer OAuth, then falls back to S3 request authentication and maps S3 errors to Iceberg error types.

State and persistence: server holds configuration and delegates durable work to handlers through filer/S3 Tables manager. Dependencies include gorilla/mux, S3 constants/context helpers, `s3err`, `s3tables`, and glog. Integration points are the S3 gateway router and all Iceberg handlers. Risks: `responseWriter.statusCode` defaults to zero when handlers only write body without explicit header; `DefaultAllow` fallback can permit unauthenticated catalog access only when S3 gateway is configured that way; route order and path validation are security-sensitive. Tests cover OAuth and path validation, with route wiring mostly indirect.
