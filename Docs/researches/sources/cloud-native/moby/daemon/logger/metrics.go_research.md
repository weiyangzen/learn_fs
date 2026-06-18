# sources/cloud-native/moby/daemon/logger/metrics.go

Purpose: declares and registers daemon logger metrics.

Important APIs/types/functions: counters `logWritesFailedCount`, `logReadsFailedCount`, and `totalPartialLogs`; `init` creates a `logger` namespace and registers it.

Control flow/state/persistence: package initialization creates global counters for failed writes, failed reads from stdio, and log entries larger than the buffer.

Dependencies/integration: used by log copier/error paths and exported through Docker metrics.

Risks: global registration side effects must run exactly once. Counter names are observable metric contracts.

Test signals: indirect through code paths that increment counters; no direct tests here.
