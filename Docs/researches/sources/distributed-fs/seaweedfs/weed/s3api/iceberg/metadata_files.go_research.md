# Research: sources/distributed-fs/seaweedfs/weed/s3api/iceberg/metadata_files.go

## sources/distributed-fs/seaweedfs/weed/s3api/iceberg/metadata_files.go

Purpose: filer-backed storage helpers for Iceberg metadata JSON files.

Important APIs and flow: `saveMetadataFile` creates a 30-second operation context, ensures the table bucket, table path segments, and `metadata` directory exist under `s3tables.TablesPath`, then writes the metadata file as a filer entry with JSON MIME metadata. `deleteMetadataFile` removes one metadata file from the derived metadata directory. `loadMetadataFile` looks up a metadata file and returns a copy of `Entry.Content`.

State and persistence: this file directly creates directory and file entries in the filer under the S3 Tables storage tree. Dependencies include `filer_pb.LookupEntry`, `CreateEntry`, `DoRemove`, filer error sentinels, `s3tables.TablesPath`, path/string utilities, and timeouts. Integration points are table create, commit, create-on-commit, stage-create template loading, and cleanup after failed updates. Risks: `saveMetadataFile` trusts `tablePath` validation to callers; concurrent ensureDir calls handle already-exists but other errors bubble; file content is stored inline in `Entry.Content`, which is suitable for metadata JSON but not large data files. Test coverage is indirect through handlers and path validation.
