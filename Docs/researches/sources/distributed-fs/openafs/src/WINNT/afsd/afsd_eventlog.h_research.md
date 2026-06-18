# sources/distributed-fs/openafs/src/WINNT/afsd/afsd_eventlog.h

## Purpose
`afsd_eventlog.h` declares the AFSD event logging interface and includes generated event-message definitions used by callers throughout the Windows cache manager.

## Important APIs, types, and functions
The header includes `afsd_eventmessages.h` and declares `LogEventMessage(WORD wEventType, DWORD dwEventID, DWORD dwMessageID)` and `LogEvent(WORD wEventType, DWORD dwEventID, ...)`.

## Control flow
There is no runtime control flow in the header. Callers include it to get message IDs and invoke the varargs logging functions implemented in `afsd_eventlog.c`.

## State and persistence behavior
The header stores no state. It exposes APIs that can write persistent EventLog registry source configuration and runtime event records when called.

## Dependencies and integration points
This header ties AFSD modules to Windows event types and the message table generated in `afsd_eventmessages.h`. Any module logging AFSD startup, service, SMB, RX, flush-volume, or shutdown diagnostics depends on this interface.

## Risks and edge cases
`LogEvent` is varargs, so the header cannot enforce that callers pass the correct substitution arguments for each message ID. Missing or stale `afsd_eventmessages.h` definitions will break either compilation or Event Viewer message resolution.

## Test signals
Build tests should confirm that all modules include this header with the generated message header available. Static checks should verify that each `LogEvent` call passes the argument count/types expected by `afsd_eventlog.c`.
