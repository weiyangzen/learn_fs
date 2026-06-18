<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/log/Logger.cpp -->
## sources/distributed-fs/beegfs/common/source/common/app/log/Logger.cpp

### Purpose
`Logger.cpp` implements the global BeeGFS logger, including topic names, stderr fallback formatting, syslog/file output, timestamp formatting, backtrace emission, and line-count based log rotation.

### Important APIs, Types, And Functions
The file defines `Logger::logger`, `Logger::LogTopics`, syslog level mapping, constructor/destructor, `logStdErr`, `logGrantedUnlocked`, `logGranted`, `logBacktraceGranted`, `getTimeStr`, `prepareLogFiles`, `rotateLogFile`, and `rotateStdLogChecked`.

### Control Flow
Construction initializes topic log levels, rwlock, time format, file pointers, and log files. Normal logging takes a read lock, writes either file/stdout or syslog, increments line count, unlocks, then checks rotation. Rotation takes a write lock, closes the current file, renames old files through suffixes, opens a new file, and resets line count. `logStdErr` provides pre-singleton fallback.

### State, Persistence, And Dependencies
Persistent artifacts are log files and rotated `.old-N` files. In-memory state includes singleton ownership, log levels, file handles, rwlock, line counters, and rotation settings. Dependencies include `StringTk`, `PThread`, `TimeAbs`, `syslog`, pthread rwlocks, and config exception types.

### Integration Points
`Logger.h` macros, `LogContext`, assertions, config, RDMA, and listeners all use this singleton. Config values determine log type, date inclusion, file path, max lines, and rotated file count.

### Risks
The rwlock favors readers, so heavy logging can delay rotation. File rotation ignores rename failures. If opening a configured file fails during construction, it throws after falling back to stdout. `logTopicFromName` compares `const char*` entries to `std::string`; this relies on overloaded comparison and should be kept clear in reviews.

### Test Signals
Tests should cover stderr fallback, file logging, syslog mode where feasible, rotation thresholds, topic name mapping, invalid log file path handling, timestamp formatting, and concurrent logging during rotation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/log/Logger.cpp -->
