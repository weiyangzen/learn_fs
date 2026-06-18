<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_tables.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_tables.go

Purpose: exposes AWS S3 Tables/Iceberg-compatible APIs on the S3 gateway, bridging HTTP target-style and REST-style requests into the `s3tables` package while using the S3 server's filer and IAM context.

Important APIs/types/functions: `S3TablesApiServer` wraps `S3ApiServer` and `s3tables.S3TablesHandler`. Setter methods configure region, account, default allow, and IAM authorizer. `registerS3TablesRoutes` installs target and REST routes. `handleRestOperation` converts REST path/query/body into target-style JSON payloads. Builder helpers create table bucket, namespace, table, policy, tag, and get-table requests. `readS3TablesJSONBody`, `writeS3TablesError`, `getDecodedPathParam`, namespace/int/tag parsers, `isS3TablesSignedRequest`, `extractCredentialScope`, and `authenticateS3Tables` provide validation and auth glue.

Control flow: registration creates the handler, wires IAM default behavior and authorizer, then registers a target-header route and REST routes gated by `serviceMatcher`. REST handlers build a typed payload, replace the request body with AWS JSON protocol content, set `X-Amz-Target`, and invoke the common S3 Tables handler. Auth wrapper authenticates signatures when IAM is enabled, stores identity in context, and delegates authorization to the S3 Tables handler.

State and persistence behavior: this file itself stores no table metadata. It passes filer access through `WithFilerClient`; actual table bucket, namespace, table, policy, and tag persistence is in the `s3tables` implementation/filer backend. It may read identity context for IAM checks.

Dependencies and integration: uses gorilla/mux, S3 IAM context constants, S3 error utilities, generated filer client, and the `s3tables` package. Route registration is called from `s3api_server.go` before regular S3 bucket routes.

Risks: route collisions are the main hazard because REST paths like `/buckets` and `/get-table` can also be regular S3 bucket names. The code deliberately requires SigV4 credential scope service `s3tables` for REST routes; weakening that matcher can hijack regular S3 traffic. Path decoding rejects traversal/NUL but individual builders must still validate table names and namespaces. Body reads are limited to 10 MiB. DefaultAllow behavior can permit unauthenticated access when IAM is disabled or permissive.

Test signals: routing tests ensure S3-signed `/buckets` and `/get-table` fall through to regular S3 while s3tables-signed requests match S3 Tables. REST validation tests ensure invalid namespace query values produce JSON `InvalidRequest` responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_tables.go -->
