## sources/cloud-native/moby/daemon/logger/copier_test.go

Purpose: Unit tests and benchmarks for copying log streams into logger implementations.

Important fixtures and tests: `TestLoggerJSON` and `TestSizedLoggerJSON` encode messages as JSON with mutex protection. `TestCopier` validates stdout/stderr complete and trailing lines. `TestCopierLongLines` verifies long lines are split at default buffer size. `TestCopierSlow` ensures `Close` lets a slow logger exit promptly. `TestCopierWithSized` checks `SizedLogger.BufSize` directly and through ring logger wrapping. `TestCopierWithPartial` verifies partial IDs, timestamps, ordinals, and final flags across stdout/stderr long chunks while normal messages lack partial metadata. Benchmarks run copier with piped data from 64 bytes to 256 KiB.

Control flow and state: Tests use JSON decoding to inspect emitted `Message` values and explicit timeout channels to catch hangs. Partial tests track expected IDs/timestamps per source.

Dependencies and integration points: Exercises `NewCopier`, logger interfaces, partial-log backend metadata, ring logger buffer sizing, and message source attribution.

Risks covered: Protects against hangs, incorrect source assignment, broken buffer sizing, and partial log metadata regressions. Timing-based tests must balance speed with avoiding flakes.
