# sources/distributed-fs/juicefs/pkg/vfs/accesslog_test.go

Purpose: verifies `.accesslog` reader lifecycle and log formatting.

Important APIs and types: `TestAccessLog` uses `openAccessLog`, `closeAccessLog`, `NewLogContext`, `logit`, and `readAccessLog`.

Control flow and state: the test opens handle 1, writes one synthetic operation, confirms reading an invalid handle returns zero, then does a partial read to ensure stored leftovers are returned without blocking. It reads the rest of the line, parses the timestamp, validates uid/gid/pid/method/error/duration formatting, and finally confirms an empty blocking read returns `#\n`.

Persistence and integration: no persistent state; it exercises in-memory access-log channels and the meta context wrapper.

Risks and test signals: the test depends on timing thresholds and exact byte counts. It covers core read semantics but not multi-reader fan-out, dropped lines under buffer pressure, slow-operation logger output, or Prometheus metric values.
