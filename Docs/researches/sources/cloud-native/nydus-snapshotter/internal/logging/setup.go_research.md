# sources/cloud-native/nydus-snapshotter/internal/logging/setup.go

Purpose: initialize process logging.

Flow: `SetUp` parses log level, configures logrus output to stdout or a lumberjack rotating file, creates log directory for file mode, and installs a timestamped text formatter compatible with containerd log timestamp format. `WithContext` returns a context using the global containerd logger.

State/dependencies: mutates global logrus logger and writes rotating logs under configured directory.

Integration points: called by main before processing/starting snapshotter; tests exercise rotation.

Risks/tests: file mode requires non-nil rotation args. Global logger mutation affects package-wide tests. Rotation test writes many log lines and asserts backup count.
