<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/log/Logger.h -->
## sources/distributed-fs/beegfs/common/source/common/app/log/Logger.h

### Purpose
`Logger.h` declares BeeGFS logging levels, topics, helper formatting types, the `Logger` singleton, and the `LOG`/`LOG_CTX` macro family.

### Important APIs, Types, And Functions
It defines `LogLevel`, `LogTopic`, `beegfs::logging::SystemError`, `InBase`, `LogInfos`, and class `Logger`. Public methods include `log` overloads, `logBacktrace`, log level getters/setters, topic name conversion, singleton create/destroy/get/isInitialized, and stderr fallback. Macros support structured key/value log items, optional level-gated items, `sysErr`, `hex`, and `oct` formatting helpers.

### Control Flow
The macro path first checks the global logger and topic threshold. It builds a message with optional structured fields, then dispatches either to the singleton or `logStdErr` if no logger exists.

### State, Persistence, And Dependencies
The class owns singleton logger state declared in the cpp file. Header dependencies include config exceptions, storage errors, atomics, pthread/threading, Boost preprocessor, Boost ios state, and system error utilities.

### Integration Points
Every file in this subset that logs uses either `LOG`, `LOG_CTX`, or `LogContext`, making this header the common logging contract.

### Risks
The macro layer is complex and compile-time fragile. `setLogLevel` and `getLogLevels` are explicitly not thread-safe. Topic enum and `LogTopics` array must stay in sync. Macros evaluate streamed values only when the level passes, but arguments must still compile.

### Test Signals
Compile tests should exercise one-, two-, and three-part structured items, topic thresholds, no-logger fallback, bool/error_code/SystemError formatting, topic string conversion, and debug macro elision.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/log/Logger.h -->
