<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/eventlog/test/elogtest.c -->
## sources/distributed-fs/openafs/src/WINNT/eventlog/test/elogtest.c

Purpose: Command-line smoke test for AFS Windows Event Log configuration and the alternate event logging functions.

Important APIs, types, and functions: `main` opens the application log registry key, checks the AFS server event source key, then calls `ReportInformationEventAlt`, `ReportWarningEventAlt`, and `ReportErrorEventAlt` with no insertion strings and with two insertion strings.

Control flow and state: If the expected event source registry keys are missing, the test prints a skip message and exits success. Otherwise it logs six test events and exits with status 1 on the first logging failure.

Persistence and dependencies: Writes test events to Windows Event Log. Depends on `WINNT/afsreg.h`, `WINNT/afsevent.h`, registry helpers such as `RegOpenKeyAlt`, and the logging implementation.

Integration points: Validates installation-time event source registration and message IDs for server test events.

Risks: Success when registry keys are absent means CI can miss broken registration if it does not assert the skip text. The test uses fixed server event IDs and ANSI insertion strings.

Test signals: Expected console lines, six Event Log entries with correct severity and insertion text, nonzero exit on logging failure, and explicit handling of missing registry keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/eventlog/test/elogtest.c -->
