# sources/cloud-native/moby/daemon/logger/jsonfilelog/jsonlog/fuzz_test.go

Purpose: fuzzes the optimized JSON marshaler for arbitrary log bytes.

Important APIs/types/functions: `FuzzJSONLogsMarshalJSONBuf` constructs `JSONLogs` with fuzzed `Log` bytes and calls `MarshalJSONBuf`.

Control flow/state/persistence: in-memory buffer only; primarily guards against panics and invalid UTF-8 edge cases.

Dependencies/integration: targets escaping code in `jsonlogbytes.go`.

Risks: semantic JSON validity is indirectly exercised but not deeply asserted in the fuzz body.

Test signals: robustness signal for the custom byte-string JSON escaping path.
