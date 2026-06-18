# sources/cloud-native/moby/daemon/logger/jsonfilelog/jsonlog/time_marshalling.go

Purpose: small optimized timestamp marshaler for json-file output.

Important APIs/types/functions: `fastTimeMarshalJSON` returns `t.Format("\""+time.RFC3339Nano+"\"")` after checking year range; `jsonFormat` stores the quoted layout.

Control flow/state/persistence: no state. It mirrors `time.Time.MarshalJSON` range behavior while avoiding an allocation.

Dependencies/integration: used by `JSONLogs.MarshalJSONBuf`.

Risks: must track Go's JSON time behavior closely. Years outside `[0,9999]` are rejected.

Test signals: `time_marshalling_test.go` compares valid output and invalid year behavior.
