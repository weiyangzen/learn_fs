# sources/cloud-native/moby/daemon/logger/jsonfilelog/jsonlog/jsonlogbytes_test.go

Purpose: validates optimized JSON marshaling output.

Important APIs/types/functions: `TestJSONLogsMarshalJSONBuf` checks generated JSON with regular expressions for log, stream, attrs, and time fields; helper `regexP` builds matchers.

Control flow/state/persistence: in-memory buffer only.

Dependencies/integration: targets `JSONLogs.MarshalJSONBuf`.

Risks: regex checks are flexible about field order or exact timestamp but may not catch every escaping mismatch.

Test signals: direct signal that generated log records include expected fields and valid-looking timestamp formatting.
