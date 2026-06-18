## sources/distributed-fs/seaweedfs/weed/s3api/s3tables/handler_table.go

Purpose: implements S3 Tables table operations for create, get, list, delete, and update. The handlers decode JSON RPC-style requests, validate bucket ARN, namespace, table name, and ICEBERG format, then map logical resources to filer paths under the table-bucket tree.

Important APIs: `handleCreateTable`, `handleGetTable`, `handleListTables`, `handleDeleteTable`, `handleUpdateTable`, `listTablesInNamespaceWithClient`, `listTablesWithClient`, and `listTablesInAllNamespaces`. Responses are built from `tableMetadataInternal` and public response types in `types.go`.

Control flow: create validates namespace existence, loads namespace and bucket policies/tags, checks either namespace or bucket permission, creates the table directory plus `data/`, then writes metadata/tags as extended attributes. Get supports lookup by table ARN or bucket/namespace/name and hides unauthorized reads as `NoSuchTable`. List handles namespace-scoped and whole-bucket listings with continuation tokens. Delete and update load metadata first, enforce optional version tokens, authorize against table or bucket policy, then delete the directory or rewrite metadata.

State and persistence: table metadata, tags, and policies live in filer extended attributes; table data lives in directories below `TablesPath/{bucket}/{namespace}/{table}`. Version tokens are regenerated on updates for optimistic concurrency.

Dependencies and integration: depends on filer gRPC list/entry operations, path/ARN helpers from `utils.go`, policy evaluation from `permissions.go`, and request identity/default-allow behavior from IAM helpers. Risks include policy fetch failures becoming 500s, list pagination edge cases across namespaces, and authorization behavior that differs between 403 and not-found hiding. Test signals are indirect through manager, permission, namespace, and layout tests.
