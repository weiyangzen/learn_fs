# sources/cloud-native/moby/daemon/logger/jsonfilelog/jsonfilelog.go

Purpose: default Docker `json-file` logging driver that writes newline-delimited JSON log records to host files with rotation support.

Important APIs/types/functions: `JSONFileLogger`, `New`, `Log`, `marshalMessage`, `ValidateLogOpt`, `Close`, and `Name`. Options include `max-size`, `max-file`, `compress`, common attrs, and tag.

Control flow/state/persistence: `New` parses rotation/compression options, gathers extra attrs and optional tag, marshals attrs once, and creates `loggerutils.LogFile`. `Log` gets a pooled buffer, appends newline to complete or non-partial messages, writes optimized JSON using `jsonlog.JSONLogs.MarshalJSONBuf`, appends record newline, and delegates persistence/rotation to `LogFile`.

Dependencies/integration: depends on `logger.Info`, `loggerutils.LogFile`, `jsonfilelog/jsonlog`, and go-units size parsing. Read support is in `read.go`; registration is in `register.go`.

Risks: compression is invalid without rotation. JSON attrs are precomputed and immutable. The json-file format does not round-trip partial metadata, only line newline behavior.

Test signals: `jsonfilelog_test.go`, read tests, and fuzz tests cover write format, options, rotation, labels/env attrs, and readback.
