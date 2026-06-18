<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/history/filter.go -->
## sources/cloud-native/buildkit/solver/llbsolver/history/filter.go

Purpose: parses and applies build history filters for refs, status, repository, timestamps, durations, and result limits.

Important APIs and types: `filterHistoryEvents`, `parseFilters`, `parseFilter`, `timeBasedFilter`, `adaptHistoryRecord`, and `cutAny`; status constants `running`, `completed`, `error`, and `canceled`.

Control flow: events are first nil-filtered. Multiple filter strings are ORed, while comma-separated fields inside one filter string are ANDed. Time filters support `startedAt`, `completedAt`, and `duration` with `>`, `>=`, `<`, `<=`; timestamp values can be durations relative to now or RFC3339 times. Static filters use containerd filter parsing over an adaptor exposing `ref`, `status`, and `repository`. Limits sort newest-first by `CreatedAt` and reject negative limits.

State and dependencies: no persistence; pure filtering over event slices. Depends on containerd filters, BuildKit git URL parsing, csvvalue parsing, and time.

Integration points: `Queue.Listen` uses this before returning completed history records.

Risks and test signals: duration comparisons convert `time.Duration` to int64 nanoseconds while timestamp comparisons use Unix seconds. Repository extraction falls back from `vcs:source` to parsed `context`. `filter_test.go` covers ref/repository/status-like time/limit/or/and/error cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/history/filter.go -->
