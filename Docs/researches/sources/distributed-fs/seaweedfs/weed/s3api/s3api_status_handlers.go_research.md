<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_status_handlers.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_status_handlers.go

Purpose: provides the minimal liveness/readiness/status handler registered for `/status`, `/healthz`, and `/readyz`.

Important APIs/functions: `StatusHandler` is an `S3ApiServer` method that writes HTTP 200 with an empty body through `s3err.WriteResponse`.

Control flow: the handler ignores request method details and server dependency health; route registration in `s3api_server.go` allows GET and HEAD.

State and persistence behavior: no state is read or written. It is a process-level HTTP reachability probe, not a filer/master readiness check.

Dependencies and integration: depends on `net/http` and the S3 error/response utility package. Registered before bucket routes.

Risks: because it always returns OK, orchestration systems may consider a server ready even when filer, IAM, master discovery, or STS dependencies are unhealthy. If stronger readiness is desired, this endpoint is too shallow.

Test signals: simple tests can assert GET/HEAD status 200 and empty body; integration tests should decide whether dependency failures need separate readiness endpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_status_handlers.go -->
