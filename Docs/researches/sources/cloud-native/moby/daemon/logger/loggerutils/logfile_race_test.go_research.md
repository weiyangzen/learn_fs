# sources/cloud-native/moby/daemon/logger/loggerutils/logfile_race_test.go

Purpose: race-focused tests for `LogFile` concurrency.

Important APIs/types/functions: tests exercise simultaneous writes, reads, follows, closes, and rotations under Go's race detector.

Control flow/state/persistence: temporary log files are manipulated concurrently to verify lock/channel ownership patterns.

Dependencies/integration: targets `LogFile`, `follow`, decoders, and platform file helpers.

Risks: race tests may be skipped or only meaningful with `-race`.

Test signals: important signal for the read-state channel and rotation locks.
