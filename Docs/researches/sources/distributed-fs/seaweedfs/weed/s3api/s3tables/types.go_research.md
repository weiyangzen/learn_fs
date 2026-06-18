## sources/distributed-fs/seaweedfs/weed/s3api/s3tables/types.go

Purpose: defines public JSON request/response and model types for S3 Tables bucket, namespace, table, policy, tagging, metadata, and error APIs.

Important types: `TableBucket`, create/get/list/delete bucket requests and responses, policy requests/responses, `Namespace`, namespace CRUD/list types, `IcebergSchema`, `IcebergMetadata`, `TableMetadata`, `Table`, table CRUD/list/update types, tag request/response types, and `S3TablesError`.

Control flow: this file contains no active control flow beyond `S3TablesError.Error`. Its struct tags define wire compatibility with the JSON RPC handler layer.

State and persistence: public types mirror persisted internal metadata from `utils.go` but are not themselves persistence logic. `json.RawMessage` in `TableMetadata.FullMetadata` allows preserving Iceberg metadata payloads that are not modeled.

Dependencies and integration: used throughout `handler_table.go`, namespace/bucket/policy/tag handlers, manager calls, and tests. Risks are schema drift between public and internal metadata, omitempty hiding empty properties/tags, and enum-like strings such as `ICEBERG` being untyped. Error code constants centralize handler response types.
