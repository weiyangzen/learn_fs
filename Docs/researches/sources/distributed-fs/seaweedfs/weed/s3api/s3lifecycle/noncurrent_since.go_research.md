# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/noncurrent_since.go

Purpose: parses the explicit noncurrent-since timestamp stamped on entries when a version is demoted.

Important API: `SuccessorFromEntryStamp(entry *filer_pb.Entry) time.Time`. It reads `s3_constants.ExtNoncurrentSinceNsKey` from `Entry.Extended`, parses it as Unix nanoseconds, and returns zero for nil, missing, empty, unparseable, or non-positive values.

Control flow/state: pure parser over entry metadata. It prefers the demotion stamp over legacy successor mtime derivation because the stamp records the actual demotion time and is immune to later sibling mtime edits.

Dependencies/integration: used by router and bootstrap walker to populate `ObjectInfo.SuccessorModTime` consistently. Depends on filer protobuf entries and S3 constants.

Risks: callers must fall back correctly on zero for legacy entries. A malformed stamp silently becomes zero, so bad writers degrade precision instead of failing routing. Nanosecond values must be decimal strings.

Test signals: `noncurrent_since_test.go` covers nil/missing/empty/invalid/non-positive values, positive nanosecond round-trip, and ordering preservation.
