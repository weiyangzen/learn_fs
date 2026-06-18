<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/Assert.cpp -->
## sources/distributed-fs/beegfs/common/source/common/Assert.cpp

### Purpose
`Assert.cpp` implements debug-build assertion failure reporting for the `ASSERT` macro in `Common.h`.

### Important APIs, Types, And Functions
Under `BEEGFS_DEBUG`, `beegfs_debug::assertMsg(file, line, condition)` formats the failed condition, captures a dynamic backtrace, logs with `LOG(GENERAL, ERR, ...)`, and exits the process.

### Control Flow
The function extracts a basename from the source file path, records the asserting thread name, captures backtrace frames with `backtrace`, grows the vector if exactly full, resolves symbols, logs, and calls `exit(1)`.

### State, Persistence, And Dependencies
There is no persistent state. It depends on `Common.h`, `AbstractApp`, `Logger`, `PThread`, `execinfo`, and streams.

### Integration Points
`Common.h` maps `ASSERT(condition)` to this function only in debug builds. Production builds compile assertions away.

### Risks
`backtrace_symbols` allocation is not freed because the process exits immediately. Logging during a failing assertion can itself depend on initialized logging/threading state.

### Test Signals
Debug-only tests can assert a child process exits nonzero and emits the failed condition plus a backtrace. Release builds should verify `ASSERT` has no side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/Assert.cpp -->
