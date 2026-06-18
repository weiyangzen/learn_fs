# sources/distributed-fs/openafs/src/util/serverLog.c

Purpose: Implements server logging, log-file rotation/reopen, signal-driven debug-level control, optional thread id logging, stdout/stderr redirection, and syslog support.

Important APIs and state: Public APIs include `OpenLog()`, `CloseLog()`, `ReOpenLog()`, `FSLog()`, `vFSLog()`, `WriteLogBuffer()`, `LogCommandLine()`, `GetLogLevel()`, `GetLogDest()`, `GetLogFilename()`, `SetLogThreadNumProgram()`, `SetupLogSignals()`, and pthread `SetupLogSoftSignals()`. Static state includes `serverLogFD`, `serverLogOpts`, `ourName`, `logTime`, `threadIdLogs`, `resetSignals`, and a pthread mutex initialized via `pthread_once`.

Control flow: `OpenLog()` copies options, sets `LogLevel`, chooses file or syslog destination, rotates on open when requested, opens append/truncate mode, redirects stdout/stderr, and stores the filename for reopen. `vFSLog()` builds a timestamp/thread prefix, formats into a fixed buffer, and writes under lock to fd or syslog. Signal handlers raise/reset debug level and reopen/rotate logs. `RenameLogFile()` supports `.old` and timestamp styles.

Dependencies and integration: Uses roken, `afsutil.h`, `fileutil.h`, LWP/procmgmt, pthread/softsig where enabled, and optional syslog. Server processes call this early during startup.

Risks and test signals: `vFSLog()` truncates messages to 1024 bytes. Traditional `.old` rotation can overwrite older logs. FIFO handling avoids rotation and opens nonblocking. Signal behavior differs between pthread soft signals and legacy LWP. Tests should cover file logging, syslog builds, rotation styles, reopen after external rotation, and debug signal changes.
