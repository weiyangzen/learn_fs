# sources/cloud-native/moby/daemon/logger/loggerutils/follow.go

Purpose: follows an active `LogFile` as new entries are written and files rotate.

Important APIs/types/functions: `follow.Do`, `nextPos`, and `forward`. The struct carries `LogFile`, watcher, decoder, forwarder, log entry, and reusable notification channel.

Control flow/state/persistence: `Do` waits for write-position updates from `LogFile.read`, forwards the new section of the current file, detects rotation by sequence number, flushes old file remainder, atomically opens the new current file under `fsopMu`, warns on missed rotations, and continues from offset zero. `nextPos` registers waiters or returns immediate updates and exits on close or consumer-gone.

Dependencies/integration: used only by `LogFile.ReadLogs` when `Follow` is true. Relies on `Decoder` and `forwarder` abstractions.

Risks: missed rotations can skip logs. Correctness depends on `LogFile` position updates and filesystem locks staying in sync.

Test signals: `logfile_test.go`, race tests, and driver read tests exercise follow across writes and rotations.
