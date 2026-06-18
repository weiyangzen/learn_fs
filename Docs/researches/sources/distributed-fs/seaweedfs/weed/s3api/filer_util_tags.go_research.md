# Research: sources/distributed-fs/seaweedfs/weed/s3api/filer_util_tags.go

## sources/distributed-fs/seaweedfs/weed/s3api/filer_util_tags.go

Purpose: helper methods for S3 object tagging stored in filer entry extended attributes. The constant `S3TAG_PREFIX` is built from `s3_constants.AmzObjectTagging + "-"`, so each tag key is persisted under a prefixed extended-attribute name.

Important APIs and flow: `getTags` looks up an entry and returns all `Extended` entries whose keys start with `S3TAG_PREFIX`, stripping that prefix. `setTags` looks up the entry, deletes any old tag-prefixed attributes, initializes `Extended` if needed, writes the new tag map, and persists via `filer_pb.UpdateEntry`. `rmTags` removes tag-prefixed attributes and avoids an update if no tag was present.

State and persistence: tags live in `filer_pb.Entry.Extended`, so object tagging changes are metadata-only filer updates. Dependencies are `WithFilerClient`, `LookupEntry`, `UpdateEntry`, `context.Background`, string prefix matching, and S3 constants. Integration points are bucket/object tagging HTTP handlers and any lifecycle/policy code that reads tag metadata. Risks: tag keys are stored verbatim after the prefix, so validation and encoding must occur at the handler layer; concurrent metadata updates could race because the whole entry is read-modify-written; nil `Extended` maps are handled on set but `getTags` assumes a valid lookup response/entry.
