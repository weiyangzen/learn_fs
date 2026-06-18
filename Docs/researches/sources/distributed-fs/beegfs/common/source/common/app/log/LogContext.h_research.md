<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/log/LogContext.h -->
## sources/distributed-fs/beegfs/common/source/common/app/log/LogContext.h

### Purpose
`LogContext` is a lightweight contextual logging helper that captures a context string and forwards messages/backtraces to the global `Logger`.

### Important APIs, Types, And Functions
It defines debug logging macros controlled by `LOG_DEBUG_MESSAGES`, backtrace array size, constructors, `log` overloads by topic/level, `logErr`, and `logBacktrace`. A protected constructor and `setLogger` support derived context providers.

### Control Flow
Construction snapshots `Logger::getLogger()`. Logging methods return silently if no logger is available. `logBacktrace` captures stack frames with `backtrace`, resolves symbols, logs them, and frees symbol storage if logging proceeds.

### State, Persistence, And Dependencies
State is a context string and raw `Logger*`. Dependencies include `Logger`, `AbstractApp`, `PThread`, `Common`, and `execinfo`.

### Integration Points
Used throughout app, config, listener, assertion, and component code for stable context names without passing logger references everywhere.

### Risks
Because the logger pointer is captured at construction, contexts created before logger initialization will not start logging later unless reset. In `logBacktrace`, if no logger exists after `backtrace_symbols`, the function returns without freeing symbols.

### Test Signals
Tests should cover logging with initialized and missing logger, context string propagation, backtrace logging, and debug macro compilation in debug and non-debug builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/log/LogContext.h -->
