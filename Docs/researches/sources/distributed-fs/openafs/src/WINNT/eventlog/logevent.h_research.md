<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/eventlog/logevent.h -->
## sources/distributed-fs/openafs/src/WINNT/eventlog/logevent.h

Purpose: Declares alternate Windows Event Log helper APIs and the insertion-string limit.

Important APIs, types, and functions: `AFSEVT_MAXARGS` is 16. Exports are `ReportErrorEventAlt`, `ReportWarningEventAlt`, and `ReportInformationEventAlt`.

Control flow and state: Callers pass event id, status where applicable, and a NULL-terminated sequence of insertion strings.

Persistence and dependencies: Persistence is through Windows Event Log in the implementation. The header itself has no external include guard dependencies beyond C types.

Integration points: Included by eventlog implementation and consumers/tests such as `elogtest.c`.

Risks: Varargs API is easy to misuse if the terminating `0` is omitted or if the event id does not match message table definitions.

Test signals: Compile callers with prototypes visible and test max argument enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/eventlog/logevent.h -->
