# sources/cloud-native/moby/daemon/logger/jsonfilelog/jsonlog/time_marshalling_test.go

Purpose: tests timestamp JSON marshaling helper.

Important APIs/types/functions: `TestFastTimeMarshalJSONWithInvalidYear` asserts range errors; `TestFastTimeMarshalJSON` asserts RFC3339Nano output.

Control flow/state/persistence: in-memory only.

Dependencies/integration: validates the timestamp path used by `JSONLogs.MarshalJSONBuf`.

Risks: limited cases, but covers the key divergence risk from `time.MarshalJSON`.

Test signals: direct confidence in valid and invalid time formatting behavior.
