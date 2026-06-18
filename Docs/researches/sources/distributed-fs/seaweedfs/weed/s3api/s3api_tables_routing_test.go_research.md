<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_tables_routing_test.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_tables_routing_test.go

Purpose: regression tests for S3 Tables route disambiguation from regular S3 routes with colliding paths.

Important APIs/functions: `TestIsS3TablesSignedRequest` tests credential-scope parsing. Routing tests use `setupRoutingTestServer`, `signRoutingTestRequest`, and mux route matching for `/buckets`, PUT `/buckets`, and `/get-table`.

Control flow: requests signed for service `s3` must not match S3 Tables REST routes, even when paths overlap; requests signed for `s3tables` must match the intended S3 Tables route.

State and persistence behavior: no persistent state. The test uses route matching rather than executing handlers, avoiding filer dependencies.

Dependencies and integration: depends on AWS SigV4 signing, mux route templates, and the route registration in `s3api_tables.go`/`s3api_server.go`.

Risks: route-template assertions rely on exact path templates. The tests intentionally require signed S3 Tables traffic; unsigned default-allow S3 Tables REST requests will not match REST routes, which is a design tradeoff for collision safety.

Test signals: passing tests mean regular S3 clients can use bucket names such as `buckets` and `get-table` without receiving S3 Tables JSON, while legitimate S3 Tables clients remain routable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_tables_routing_test.go -->
