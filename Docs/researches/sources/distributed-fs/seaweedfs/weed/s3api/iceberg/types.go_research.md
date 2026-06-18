# Research: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/types.go

## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/types.go

Purpose: wire types for Iceberg REST Catalog requests/responses and custom JSON handling around `iceberg-go` metadata.

Important types: `CatalogConfig`, `ErrorModel`, `ErrorResponse`, `Namespace`, `TableIdentifier`, namespace/table list/create/get responses, `CreateTableRequest`, `LoadTableResult`, `CommitTableRequest`, and `CommitTableResponse`. `CreateTableRequest` embeds `iceberg.Schema`, `PartitionSpec`, `table.SortOrder`, stage-create, and properties. `LoadTableResult.MarshalJSON` and `CommitTableResponse.MarshalJSON` serialize `table.Metadata`, run `ensureMetadataSpecCompliance`, and embed raw metadata JSON. Their `UnmarshalJSON` counterparts parse metadata with `table.ParseMetadataBytes`.

State and persistence: types are transient request/response structs, but their marshaled metadata bytes are also used by handlers for persistence. Dependencies include `iceberg-go` and `iceberg-go/table`. Integration points are every Iceberg HTTP handler and strict clients expecting REST spec field names like `metadata-location` and `next-page-token`. Risks: custom marshal must stay in sync with Iceberg spec and `iceberg-go` parser behavior; `table.Metadata` as an interface-like type can fail marshal/parse at runtime; omitting config on commit responses is intentional but client expectations may vary. Tests for metadata compliance indirectly validate the custom marshal fixup.
