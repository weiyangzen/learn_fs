<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/logging.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/logging.h

## Purpose
Declares libhdfspp logging levels, components, macros, logger interfaces, global manager, default stderr logger, and `LogMessage` streaming API.

## Important APIs, Types, And Functions
`LogLevel` covers trace through error. `LogSourceComponent` is a bitmask for unknown, RPC, block reader, file handle, file system, and async runtime. Macros `LOG_TRACE` through `LOG_ERROR` guard construction. `LoggerInterface`, `StderrLogger`, `LogManager`, and `LogMessage` define the logging extension points and message metadata.

## Control Flow
Macros call `LogManager::ShouldLog`; implementation writes through the active logger in `logging.cc`.

## State And Persistence
Static manager state is declared here and defined in the implementation. Messages are stack temporaries emitted at destruction.

## Dependencies And Integration Points
Every native subsystem includes this header for diagnostics. The C binding maps public log constants to these internal enums.

## Risks
The macro form requires call sites to use the unusual `LOG_INFO(component, << "text")` pattern. Direct `LogMessage` construction bypasses filtering. Component values must remain aligned with public C API validation.

## Test Signals
Compile tests should cover every macro and overload; integration tests should validate public component and level constants against this enum.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/logging.h -->
