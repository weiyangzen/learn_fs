# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_tagging.go

Purpose: this file implements GET, PUT, and DELETE object tagging handlers for regular and versioned objects. It converts between S3 tagging XML and SeaweedFS extended attributes using the shared `S3TAG_PREFIX` convention.

Important APIs/types/functions: handlers are `GetObjectTaggingHandler`, `PutObjectTaggingHandler`, and `DeleteObjectTaggingHandler`. They use `Tagging`, `FromTags`, `ValidateTags`, `isVersioningConfigured`, `getSpecificObjectVersion`, `getLatestObjectVersion`, `getTags`, `setTags`, `rmTags`, `filer_pb.UpdateEntry`, and table bucket path validation.

Control flow: all handlers parse bucket/object and reject invalid table-bucket paths. GET checks versioning configuration; for versioned buckets it resolves a specific or latest version, rejects delete markers, extracts `S3TAG_PREFIX` extended attributes, and returns XML. For non-versioned buckets it delegates to `getTags`. PUT reads and XML-unmarshals a bounded body, validates tags, resolves versioning, then either delegates to `setTags` for non-versioned objects or mutates the resolved entry's extended attributes and updates the correct filer directory. DELETE follows the same version resolution and either calls `rmTags` or removes prefixed extended attributes and updates the entry.

State and persistence behavior: non-versioned tag state is managed through helper functions over the regular object entry. Versioned tag state is embedded in the target version entry's `Extended` map and persisted with `UpdateEntry`; version ID `null` maps to the bucket directory, while real version IDs map to `<bucketDir>/<object>.versions`. Latest-version operations infer storage location from `ExtVersionIdKey`.

Dependencies and integration points: integrates with versioned object resolution, delete-marker semantics, filer gRPC updates, XML tag parsing, and `s3_constants.AmzObjectTagging` used by `putToFiler` when tags arrive during upload. It shares the same tag prefix storage convention as `filer_util_tags.go`.

Risks: update-directory derivation uses the object string directly; callers rely on normalized object paths from routing. Concurrent tag updates can overwrite unrelated extended attribute mutations because the handler updates the whole entry returned earlier. The versioned path has duplicated directory-selection logic in PUT and DELETE, increasing maintenance risk. DELETE returns success when no tags exist, which matches S3-style idempotence.

Test signals: this subset does not include a direct tagging test file, but `put.go` stores upload-time tags and post-policy tests ensure `x-amz-tagging` can be forwarded to the write path. Dedicated tests should cover versioned tag update/delete, delete-marker rejection, and concurrent extended-metadata preservation.
