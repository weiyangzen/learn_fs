# sources/cloud-native/moby/daemon/logger/jsonfilelog/read.go

Purpose: implements `logger.LogReader` for json-file logs.

Important APIs/types/functions: `ReadLogs` delegates to `LogFile.ReadLogs`; `decodeLogLine` turns one decoded `jsonlog.JSONLog` into `logger.Message`; `decoder` wraps `json.Decoder`; `decodeFunc` constructs it; `getTailReader` delegates line tailing to `tailfile.NewTailReader`.

Control flow/state/persistence: records are newline-delimited JSON. The decoder resets and reuses a `JSONLog`, converts attrs map to backend attrs slice, and returns line bytes as stored. Tail scanning is text-line based.

Dependencies/integration: depends on `loggerutils.LogFile`, `jsonfilelog/jsonlog`, backend attrs, and `pkg/tailfile`.

Risks: malformed JSON returns decoder errors; `LogFile` treats decode errors while tailing rotated files as warnings and moves on. Partial metadata is not persisted.

Test signals: `read_test.go`, `loggertest.Reader`, and fuzz tests validate decoding, tailing, rotation, and follow behavior.
