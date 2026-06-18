# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/ha/StreamPumper.java

Purpose: Asynchronously drains subprocess output streams and forwards lines into SLF4J logs, preventing fencer subprocesses from blocking on full stdout/stderr pipes.

Important APIs and types: Package-private `StreamPumper`, enum `StreamType` (`STDOUT`, `STDERR`), constructor, `start()`, `join()`, and protected `pump()`.

Control flow: Construction creates a daemon `SubjectInheritingThread`. `start()` begins the thread; `pump()` reads UTF-8 lines from the input stream and logs stdout at INFO or stderr at WARN with a prefix; `join()` waits for completion. Any pump exception is logged through `ShellCommandFencer.LOG`.

State and persistence: Holds logger, prefix, stream type, input stream, thread, and `started` flag. No persistence.

Dependencies and integration points: Used by `ShellCommandFencer`, `SshFenceByTcpPort`, and `PowerShellFencer`. Uses `SubjectInheritingThread` so security subject context is inherited by logging thread.

Risks: `join()` and `start()` rely on assertions for lifecycle misuse; assertions may be disabled. It never explicitly closes the stream. Very verbose commands can flood logs. Exceptions are logged to `ShellCommandFencer.LOG` even when used by other fencers.

Test signals: Fencer tests should verify stdout/stderr draining, log levels, daemon thread behavior, and no subprocess deadlock with large output.
