# Research: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/handlers_commit.go

## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/handlers_commit.go

Purpose: HTTP handler for Iceberg REST Catalog table commit (`POST /v1/.../tables/{table}`), mapping REST commit requests to S3 Tables catalog updates and filer metadata file writes.

Control flow: `handleUpdateTable` parses namespace/table, resolves bucket ARN and identity, decodes raw requirements/updates, separates statistics updates, then attempts up to three commits. It first loads the table through S3 Tables. If not found and stage-create/assert-create allows creation, it optionally loads the latest stage marker and staged metadata template, validates requirements, creates base metadata if needed, and delegates to `finalizeCreateOnCommit`. For existing tables it parses current full metadata or creates synthetic metadata, validates requirements, applies updates via `MetadataBuilderFromBase`, serializes, applies statistics and spec compliance, writes `v{version+1}.metadata.json`, then calls S3 Tables `UpdateTable` with the version token. Version conflicts trigger metadata cleanup, jittered retry, and eventually `CommitFailedException`.

State and persistence: writes metadata JSON under the table location, updates S3 Tables rows with version token and `FullMetadata`, and cleans orphan metadata on update failures. Dependencies include mux vars, `iceberg-go/table`, `s3tables.Manager`, filer client, path/location helpers, stage-create helpers, and S3 identity context. Risks include partial failure between file write and catalog update, requirement validation against synthetic metadata, retry races, and error classification by string. Test coverage is mostly indirect via commit update helpers.
