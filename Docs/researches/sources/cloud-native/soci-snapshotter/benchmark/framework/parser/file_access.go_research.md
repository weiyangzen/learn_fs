# sources/cloud-native/soci-snapshotter/benchmark/framework/parser/file_access.go

Purpose: parses SOCI benchmark logs to summarize FUSE file access patterns relative to container task start time.

Important APIs/types/functions: package `bparser`; `FileAccessPatterns`, `SociLog`, `BaseOperation`, `Operation`, `ParseFileAccesses`, and `getTaskStartTime`.

Control flow: `ParseFileAccesses` obtains task start time from containerd logs, scans SOCI stderr JSON lines, filters messages equal to `FUSE operation`, groups by operation+path, records first access offset and count, totals operations by type, sorts operations by first access time, and writes per-image JSON under `file_access_logs`. `getTaskStartTime` scans containerd stderr for `/tasks/start` and parses the leading `time=` field.

State and persistence: reads `./output/soci-snapshotter-stderr` and `containerd-stderr`; writes `./output/file_access_logs/<image>_access_patterns`.

Dependencies/integration: intended for benchmark parser tooling and SOCI FUSE log format.

Risks: scanner assumes every SOCI log line is JSON and every containerd start line has a specific text format. If no task start is found, zero time is returned without explicit error. Keying by concatenated operation+path can theoretically collide.

Test signals: parser tests with representative log lines, malformed JSON, no start line, duplicate operations, and sort order.
