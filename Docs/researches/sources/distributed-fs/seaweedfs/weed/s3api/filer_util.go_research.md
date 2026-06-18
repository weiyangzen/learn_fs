# Research: sources/distributed-fs/seaweedfs/weed/s3api/filer_util.go

## sources/distributed-fs/seaweedfs/weed/s3api/filer_util.go

Purpose: S3 API helper methods wrapping SeaweedFS filer CRUD operations for directories, files, listings, deletes, entry lookup/update, bucket collection naming, and object-key normalization.

Important APIs: `mkdir`, `mkFile`, `list`, `rm`, `rmObject`, `exists`, `getEntry`, `updateEntry`, `getCollectionName`, and `objectKey`. `doDeleteEntry` builds `filer_pb.DeleteEntryRequest` with `IgnoreRecursiveError=true`. `deleteObjectEntry` adds S3-specific handling for non-empty directory-marker deletes: when filer reports `MsgFailDelNonEmptyFolder`, it calls `demoteDirectoryMarkerToImplicitDirectory`. That function looks up the entry, verifies it is a directory key object, clears object-facing metadata, and updates the entry so the path remains as an implicit directory rather than a delete-blocking zero-byte object.

State and persistence: methods operate through `WithFilerClient` and persist `filer_pb.Entry` mutations in the filer. `clearDirectoryMarkerMetadata` removes MIME, MD5, file size, content, chunks, and public S3 extended metadata, retaining only `xattr-*` and SeaweedFS internal keys. Dependencies include `filer_pb`, `filer`, `glog`, `util.FullPath`, gRPC status codes, and S3 constants. Integration points are object delete handlers, bucket/object path logic, and callers that expect S3 directory marker semantics. Risks: error-string matching for non-empty-folder detection is brittle, context uses `context.Background`, and metadata filtering must not accidentally drop internal replication/system attributes.
