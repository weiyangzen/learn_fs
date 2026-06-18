# sources/cloud-native/buildkit/client/filter.go

Purpose: small shared option adapter that applies filter strings to multiple client APIs.

Important APIs/types/functions: `WithFilter` returns `Filter`; `Filter` implements `SetDiskUsageOption`, `SetPruneOption`, and `SetListWorkersOption`.

Control flow: each setter assigns the filter slice to the corresponding option struct.

State and persistence: no persistence; the caller-owned slice is assigned directly.

Dependencies/integration points: ties disk usage, prune, and list-workers option systems together.

Risks/test signals: direct slice assignment means subsequent caller mutation could affect options if reused before request construction. No direct tests in this subset.
