# sources/cloud-native/moby/daemon/logger/jsonfilelog/jsonlog/jsonlogbytes.go

Purpose: optimized reflection-free JSON writer for json-file log records.

Important APIs/types/functions: `JSONLogs` carries byte log, stream, created timestamp, and raw attrs. `MarshalJSONBuf` writes object fields manually. `ffjsonWriteJSONBytesAsString` escapes bytes as JSON strings, handling control bytes, quotes, backslashes, invalid UTF-8, and U+2028/U+2029.

Control flow/state/persistence: writes into caller-provided `bytes.Buffer`; emits `time` always, optional `log`, `stream`, and raw `attrs`. It trusts `RawAttrs` to already be valid JSON.

Dependencies/integration: used by `jsonfilelog.marshalMessage` and benchmarks. `fastTimeMarshalJSON` handles timestamp formatting.

Risks: custom JSON escaping must remain byte-for-byte compatible with `encoding/json` expectations. Raw attrs bypass escaping and must be produced by trusted `json.Marshal`.

Test signals: `jsonlogbytes_test.go` and fuzz tests cover escaping and structural output.
