# Research: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/handlers_namespace.go

## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/handlers_namespace.go

Purpose: Iceberg REST namespace and config handlers. They adapt REST namespace operations to S3 Tables manager calls and return Iceberg-shaped JSON.

Important APIs: `handleConfig` returns catalog defaults/overrides and, when `?warehouse=s3://bucket/...` is supplied, sets `overrides.prefix` to the bucket and echoes the warehouse. `handleListNamespaces` parses pagination and optional parent namespace, then calls `ListNamespaces`. `handleCreateNamespace` validates request body, normalizes properties, calls `CreateNamespace`, and returns properties with a default `location`. `handleGetNamespace`, `handleNamespaceExists`, and `handleDropNamespace` wrap get/head/delete with Iceberg error status mapping.

State and persistence: namespace data is persisted by S3 Tables manager in filer-backed metadata. The handlers themselves are stateless, using identity from request context and bucket resolution from prefix/warehouse/env. Dependencies include `s3tables`, `filer_pb`, mux, JSON, pagination helpers, namespace property helpers, and glog. Integration points are Iceberg clients such as DuckDB/Trino that use `/v1/config`, namespace listing, and namespace locations for table creation. Risks: error mapping still relies partly on strings; parent namespace flattening uses dot-separated S3 Tables prefixes; warehouse subpaths are intentionally ignored for bucket routing.
