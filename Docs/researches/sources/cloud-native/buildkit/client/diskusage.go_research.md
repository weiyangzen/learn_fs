# sources/cloud-native/buildkit/client/diskusage.go

Purpose: public client API for querying BuildKit disk usage and converting control API records into client-facing `UsageInfo` structures.

Important APIs/types/functions: `UsageInfo` exposes ID, mutability, in-use status, size, timestamps, usage count, parent IDs, description, record type, and shared status. `Client.DiskUsage` accepts `DiskUsageOption`s, calls `ControlClient().DiskUsage`, converts protobuf records, and sorts output. `DiskUsageInfo`, `DiskUsageOption`, `WithAgeLimit`, and `UsageRecordType` define option and record-type contracts.

Control flow: options mutate a `DiskUsageInfo`; request sends filters and age limit nanoseconds; response records are mapped one by one, including nil-safe `LastUsedAt`; slice is sorted ascending by size then ID.

State and persistence: no local persistence; reflects remote BuildKit worker/cache state at query time.

Dependencies/integration points: BuildKit control API, protobuf timestamp conversion, shared `Filter` option from `filter.go`, and `cmp`/`slices` for deterministic ordering.

Risks/test signals: age limit uses raw `time.Duration` int64, so units must match server expectations. Sorting by ascending size may be API-observable. No direct test in this subset; consumers rely on control API integration tests elsewhere.
