# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/logging_test.cc

## Purpose

This unit test validates libhdfspp logging level filtering, component masking, C forwarding, and message text propagation.

## Important APIs, types, and functions

The file defines `log_state`, `process_log_msg()`, reset/assert helpers, `log_all_components_at_level()`, and tests `MaskAll`, `MaskOne`, `Levels`, and `Text`. It installs a `CForwardingLogger` callback into `LogManager`.

## Control flow, state, and persistence

The forwarding callback records counts by level and component plus the latest message. Mask tests disable/enable components and emit logs at known levels. Level tests step through `kError`, `kWarning`, `kInfo`, `kDebug`, and `kTrace` thresholds. Runtime logging state is global in `LogManager` and reset manually by test helper calls.

## Dependencies and integration points

The file includes `bindings/c/hdfs.cc` and `common/logging.h`, plus gtest/gmock. It validates the C-facing logger bridge used by applications that register log callbacks through the binding.

## Risks and test signals

Global logging state can leak between tests if not reset carefully. The test protects behavior for component masks (`kUnknown`, `kRPC`, `kBlockReader`, `kFileHandle`, `kFileSystem`) and level ordering. It does not deeply test concurrency or logger replacement races.
