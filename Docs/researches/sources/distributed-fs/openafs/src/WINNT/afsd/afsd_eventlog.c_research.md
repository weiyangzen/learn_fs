# sources/distributed-fs/openafs/src/WINNT/afsd/afsd_eventlog.c

## Purpose
`afsd_eventlog.c` implements AFSD Windows Event Log registration and message reporting. It ensures the OpenAFS client event source exists in the registry, formats substitution strings for known message IDs, rate-limits duplicate events, and calls `ReportEvent`.

## Important APIs, types, and functions
Internal helpers are `GetServicePath` and `AddEventSource`; `GetServicePath` reads the service `ImagePath` but is not used by the active logging path. Public functions are `LogEventMessage` and `LogEvent`. `LogEventMessage` formats a system message for a Win32 error code and delegates to `LogEvent`.

`LogEvent` accepts an event type, message ID, and varargs whose expected shape depends on the message ID. It handles startup/running messages, flush-volume messages, SMB diagnostics, RX/server status messages, service stop/error messages, crypt status, and dirty-buffer shutdown messages.

## Control flow
Before each log attempt, `LogEvent` calls `AddEventSource`. That function lazily opens or creates the Application EventLog registry key and the AFSD source subkey, writes `EventMessageFile` as `afsd_service.exe`, and writes supported event types. It caches success/failure with static `bOnce` and `bRet`.

`LogEvent` registers the event source, builds up to eight substitution strings based on a switch over `dwEventID`, then uses a named mutex to compare the event with the last logged event. Consecutive duplicates with matching type, ID, argument count, and argument strings are suppressed for five seconds. Non-suppressed events are sent to `ReportEvent` and the source handle is deregistered.

## State and persistence behavior
Persistent state is written to `HKLM` under the Windows EventLog Application tree for the AFSD event source. Runtime state includes static cached event-source setup status and last-message fields used for duplicate suppression. The named mutex `AFSD Event Log Mutex` coordinates duplicate suppression across threads in the process and potentially across processes using the same name.

## Dependencies and integration points
The file depends on Windows registry and event-log APIs, `strsafe.h`, OpenAFS registry constants, AFSD service names from `afsd.h`, message IDs from `afsd_eventmessages.h`, and version/interface globals such as `AFSVersion`, `smb_Enabled`, and `RDR_Initialized`. It is used by AFSD service, flush-volume, SMB, RX, and shutdown paths that need Event Log diagnostics.

## Risks and edge cases
Creating or updating the event source requires registry permissions; failure causes logging to silently return. `EventMessageFile` is hard-coded to `afsd_service.exe` instead of using `GetServicePath`, so unusual install layouts may not resolve message text. Varargs are message-ID-dependent and unchecked by the compiler, so mismatched callers can corrupt formatting. Fixed 128-byte temporary strings may truncate large values. Duplicate suppression state is protected only around the comparison/update block; callers still pay setup/register cost. The update loop for `lpLastStrings` appears to use `i` as the loop variable while initializing `j`, so changed-argument copying should be reviewed carefully.

## Test signals
Tests should verify registry source creation with and without permissions, `ReportEvent` calls for each message-ID argument shape, system error formatting through `LogEventMessage`, startup/running substitution strings for SMB/RDR combinations, duplicate suppression within and after five seconds, and vararg formatting for server/RX/SMB/dirty-buffer messages. Installation tests should confirm that Event Viewer resolves messages from the configured message file.
