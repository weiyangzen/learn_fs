<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_version_id.go -->
# sources/distributed-fs/seaweedfs/weed/s3api/s3api_version_id.go

Purpose: defines S3 object version ID generation, validation, format detection, timestamp extraction, ordering, and helper paths for versioned object storage.

Important APIs/functions: `isValidVersionID` validates opaque client version IDs as safe path segments. `generateVersionId` creates 32-character IDs from a 16-hex timestamp prefix plus 8 random bytes, using either old raw timestamps or new inverted timestamps. `isNewFormatVersionId`, `getVersionTimestamp`, and `compareVersionIds` distinguish and sort old/new/null versions. `getVersionedObjectDir`, `getVersionFileName`, `getVersionIdFormat`, and `generateVersionIdForObject` map versions into `.versions` directories and choose format based on existing metadata.

Control flow: new format IDs use `math.MaxInt64 - now` so lexicographic order sorts newest first. Old format IDs sort newest first by reversing raw timestamp lexicographic comparison. Mixed formats compare extracted real timestamps. `getVersionIdFormat` reads the object's `.versions` directory and uses `ExtLatestVersionIdKey` metadata to preserve old-format continuity, defaulting to new format when no directory/metadata exists.

State and persistence behavior: version IDs become filenames under `.versions` via `v_<versionId>`. Format selection depends on persisted filer metadata in the `.versions` directory. Random suffix avoids collisions for same-nanosecond writes. Invalid/path-traversal version IDs are rejected by segment validation.

Dependencies and integration: uses crypto/rand, timestamp math, S3 constants for `.versions` and metadata keys, and S3 server path helpers. It is consumed by versioned object put/list/delete logic elsewhere.

Risks: format threshold assumes old raw nanoseconds remain below `0x4000...` and new inverted timestamps remain above it for relevant eras. Random-read failure falls back to zero suffix, increasing collision risk. Mixed-format compare returns equal when timestamps match, ignoring random suffix ordering. Format inference from latest metadata can choose new format for old directories missing metadata.

Test signals: version ID tests cover format detection, safe path validation, generation lengths, timestamp extraction, old/new/mixed sorting, null ordering, backward compatibility, and transition behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/s3api/s3api_version_id.go -->
