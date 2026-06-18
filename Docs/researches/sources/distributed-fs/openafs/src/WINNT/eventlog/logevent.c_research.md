<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/eventlog/logevent.c -->
## sources/distributed-fs/openafs/src/WINNT/eventlog/logevent.c

Purpose: Provides alternate AFS Windows Event Log helper functions for error, warning, and informational events with variable insertion strings and optional raw status data.

Important APIs, types, and functions: `ReportEventAlt` is the internal helper that opens the event source `AFSREG_SVR_APPLOG_SUBKEY`, calls `ReportEvent`, deregisters, and returns 0/-1. `ReportErrorEventAlt` and `ReportWarningEventAlt` collect up to `AFSEVT_MAXARGS` insertion strings and pass the status as raw event data when nonzero. `ReportInformationEventAlt` collects insertion strings and reports information events with no status data.

Control flow and state: Public functions parse a NULL-terminated varargs string list into a fixed array. If the caller supplies more than `AFSEVT_MAXARGS`, the function returns `-1` without logging. Each log call independently registers and deregisters the event source.

Persistence and dependencies: Events are persisted by Windows Event Log. Dependencies include Win32 Event Log APIs, `WINNT/afsreg.h`, and the event source registry being configured.

Integration points: Used by server-side tools or services that need to write AFS event messages. The test program `elogtest.c` exercises these APIs with event IDs from `WINNT/afsevent.h`.

Risks: The insertion string array is `char **` and uses ANSI strings. Passing non-NULL-terminated varargs can read past the intended list. `ReportEventAlt` passes `&status` even when raw data size is zero; Windows should ignore it, but it is still a notable convention.

Test signals: Registry-present and registry-missing tests, zero/two insertion strings, max-argument boundary, status raw data presence, and Event Viewer message rendering for configured message DLLs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/eventlog/logevent.c -->
