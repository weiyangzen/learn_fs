# sources/distributed-fs/openafs/src/ptserver/error_macros.h

## Purpose
Defines a convenience macro for audited process exit in protection tools.

## Important APIs, Types, And Functions
`PT_EXIT(evalue)` calls `osi_audit(PTS_ExitEvent, evalue, AUD_END)` and then `exit(evalue)`.

## Control Flow
Any caller using the macro records an audit event before terminating the process with the supplied status.

## State And Persistence
Persistent state is external audit output produced by `osi_audit`; process termination follows immediately.

## Dependencies And Integration Points
Depends on audit symbols `PTS_ExitEvent` and `AUD_END`, plus `osi_audit` and `exit`. It integrates command/tool exits with OpenAFS auditing.

## Risks And Test Signals
Risks include macro multi-statement behavior, hidden control flow, and missing audit definitions. Test signals are audited exits with expected status and clean compilation at use sites.
