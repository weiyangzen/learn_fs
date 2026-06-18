# sources/distributed-fs/seaweedfs/weed/s3api/s3api_object_handlers_copy_mime_test.go

Purpose: tests CopyObject metadata directive behavior for MIME type, system headers, user metadata, and tags. It protects S3 compatibility for COPY versus REPLACE semantics and backward compatibility with legacy non-canonical metadata keys.

Important coverage includes `TestResolveDestinationMime`, `TestIsValidDirective`, multiple `TestProcessMetadataBytes_*` cases, `TestIsManagedCopyMetadataKey_*`, and `TestMergeCopyMetadata_*`. These directly exercise `resolveDestinationMime`, `isValidDirective`, `processMetadataBytes`, `mergeCopyMetadata`, and `isManagedCopyMetadataKey`.

Control flow covers COPY keeping source MIME regardless of request Content-Type, REPLACE using request Content-Type or `binary/octet-stream`, uppercase-only directive validation, REPLACE dropping stale system/user metadata not re-specified, COPY promoting legacy case variants to canonical system/tag keys, deterministic canonical-wins behavior despite Go map iteration order, and tag replacement dropping old tags while preserving unrelated metadata.

State and persistence are in-memory `http.Header` values and metadata maps. The behavior maps directly to filer `Entry.Attributes.Mime` and `Entry.Extended` fields in `CopyObjectHandler`.

Dependencies include `copyReplaceSystemHeaders`, `s3_constants` through implementation helpers, tag parsing/validation helpers, and Go HTTP header canonicalization. Integration point is metadata construction before destination persistence and metadata-only self-copy updates.

Risks: these tests do not perform a full HTTP CopyObject request, so they do not validate response headers or filer writes. They strongly cover the pure functions where most metadata regressions happen, including stale managed key leakage and legacy casing collisions.
