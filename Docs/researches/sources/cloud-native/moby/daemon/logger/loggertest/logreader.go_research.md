# sources/cloud-native/moby/daemon/logger/loggertest/logreader.go

Purpose: reusable conformance harness for `logger.LogReader` implementations.

Important APIs/types/functions: `Reader` with `Factory`; methods `TestTail` and `TestFollow`; helpers for logging test messages, reading watchers, and syncing loggers. `compareLog` tolerates millisecond timestamp loss and ignores partial metadata where drivers do not expose it.

Control flow/state/persistence: factories create live and restarted logger instances for the same container. Tests write ordered and non-monotonic timestamp messages, then assert tail, since, until, follow from empty logs, attach mid-stream, cancellation, and high-rate no-drop behavior.

Dependencies/integration: used by json-file, local, journald, or other read-capable drivers. Relies on `logger.LogWatcher` consumer-gone behavior.

Risks: harness assumes a driver can read back messages from previous instances when testing stopped containers. Time thresholding can hide sub-millisecond precision differences intentionally.

Test signals: high-value cross-driver behavioral contract for readback APIs.
