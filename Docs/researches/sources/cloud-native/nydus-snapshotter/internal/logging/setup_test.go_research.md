# sources/cloud-native/nydus-snapshotter/internal/logging/setup_test.go

Purpose: tests logging setup and rotation behavior.

Flow: removes test log dir, configures stdout mode with nil rotation args, asserts file mode rejects nil rotation args, configures file mode with 1 MB max size and 5 backups, writes 100k log lines, then counts `.log.gz` backups.

State/dependencies: creates/removes local `test-rotate-logs`; mutates global logrus output.

Integration points: verifies the runtime logging setup used by `containerd-nydus-grpc`.

Risks/signals: backup count can be timing/filesystem sensitive. The test does not reset logger output after completion.
