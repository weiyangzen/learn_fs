<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/status.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/status.cc

## Purpose
Implements libhdfspp `Status`, including generic error codes, server exception mapping, retry classification, string formatting, and factory helpers.

## Important APIs, Types, And Functions
Known Hadoop exception class names map to internal codes such as access control, not-a-directory, snapshot protocol, standby, authentication failed, path not found, file exists, and non-empty directory. Factories include `OK`, `InvalidArgument`, `PathNotFound`, `ResourceUnavailable`, `PathIsNotDirectory`, `Unimplemented`, `Exception`, `Error`, `AuthenticationFailed`, `AuthorizationFailed`, `Canceled`, `InvalidOffset`, and `MutexError`. `ToString` and `notWorthRetry` expose status behavior.

## Control Flow
Constructors store code/message/exception class and remap recognized server exception classes. `Exception` maps Java exception names to more specific status categories where possible. `notWorthRetry` checks a static set of permission/auth-related codes.

## State And Persistence
Each `Status` owns its code, message, and exception class strings. Static maps/sets live for process lifetime. No durable state exists.

## Dependencies And Integration Points
Used throughout libhdfspp and converted to `errno` by the C binding. Retry policy, filesystem operations, RPC, and block readers all depend on consistent codes.

## Risks
`MutexError` constructs a formatted string but returns `msg`, losing the prefix. `kInvalidOffset` is later mapped oddly in `hdfs.cc` to its numeric status code as errno. Exception mappings are incomplete and require maintenance as Hadoop server exceptions evolve.

## Test Signals
Tests should cover every factory, Java exception remapping, `ToString`, retry classification, C errno mapping, unknown exceptions, null messages, and `MutexError` formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/status.cc -->
