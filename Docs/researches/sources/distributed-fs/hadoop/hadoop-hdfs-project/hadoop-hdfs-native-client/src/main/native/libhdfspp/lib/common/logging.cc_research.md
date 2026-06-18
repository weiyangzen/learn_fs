<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/logging.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/logging.cc

## Purpose
Implements libhdfspp's lightweight logging backend, including global log filtering, default stderr formatting, and streamed message construction.

## Important APIs, Types, And Functions
`LogManager` owns static `logger_impl_`, `impl_lock_`, `component_mask_`, and `level_threshold_`. It implements component enable/disable, level setting, message writing, and logger replacement. `StderrLogger::Write` formats metadata and message text. `LogMessage` destructor emits the message and overloads `operator<<` for strings, booleans, integers, pointers, endpoints, and thread IDs.

## Control Flow
Logging macros check `LogManager::ShouldLog` before constructing a `LogMessage`. The temporary accumulates text through stream-like operators, then destructor calls `LogManager::Write`. The default logger prints to stderr with level, component, timestamp, thread id, file path, line, and text.

## State And Persistence
Logging configuration is process-global and protected by a mutex. Messages are transient; the default sink writes to stderr only. C bindings can replace the logger with a callback-forwarding implementation.

## Dependencies And Integration Points
Used throughout libhdfspp common, RPC, filesystem, reader, connection, and C binding code. Integrates with `hdfsSetLogFunction`, component masks, and public log constants.

## Risks
`ShouldLog` locks on every enabled/disabled check, which can affect hot paths. `StderrLogger::Write` uses `std::localtime`, which is not thread-safe, although calls are serialized by the log manager. `operator<<(const std::string*)` streams the pointer value instead of dereferencing the string, likely surprising. Logger callbacks execute under the global logging lock and can deadlock if they re-enter logging.

## Test Signals
Tests should verify level/component filtering, stderr formatting, custom logger replacement, C callback forwarding, multithreaded logging, null string handling, and no recursive logging deadlocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/logging.cc -->
