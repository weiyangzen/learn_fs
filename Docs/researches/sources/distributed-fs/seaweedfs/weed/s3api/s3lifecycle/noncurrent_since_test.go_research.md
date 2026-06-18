# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/noncurrent_since_test.go

Purpose: direct coverage for `SuccessorFromEntryStamp`, the canonical parser for noncurrent demotion timestamps.

Important tests: nil entry, missing extended map, and empty map return zero. Nil, empty, and non-numeric raw values return zero. `"0"` and negative values return zero. A positive nanosecond string round-trips to `time.Unix(0, ns)`. Ordered nanosecond stamps produce non-decreasing parsed times.

Control flow/state: pure parser tests using fixed constants to avoid wall-clock monotonic artifacts. No persistence.

Dependencies/integration: imports filer protobufs and `ExtNoncurrentSinceNsKey`.

Risks/gaps: tests do not cover overflow values explicitly; `strconv.ParseInt` errors would fall into invalid/zero behavior. The ordering test uses fixed consecutive ns values, which is appropriate for parser properties.

Test signals: strong branch coverage for safe fallback semantics shared by router and bootstrap walker.
