<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxdebug_conns.c -->
# sources/distributed-fs/openafs/src/libadmin/samples/rxdebug_conns.c

## Purpose
Demonstrates listing RX debug connection records from a target service.

## Important APIs, Types, And Functions
It uses `util_RXDebugSupportedStats` to detect supported connection detail, `util_RXDebugConnectionsBegin/Next/Done` to iterate, and `afsclient_RXDebugOpenPort/Close` for the debug handle. Local output structures include connection details and supported-value flags.

## Control Flow
After parsing and opening the RX debug handle, the sample queries supported stats, starts the connection iterator, optionally retries with a reduced detail request if the target cannot provide all connection data, prints each connection's host/port/cid/call/security/user fields, closes the iterator, and closes the handle.

## State And Persistence
No persistent changes occur. Runtime state consists of an iterator and one current connection record.

## Dependencies And Integration Points
It integrates with RX debug service APIs and uses support discovery to adapt to older or limited RX implementations. It is linked by the libadmin samples makefile.

## Risks And Test Signals
Compatibility risk centers on supported-stat negotiation and struct-version assumptions. Tests should include a service with active and idle connections, unsupported extended stats, iterator completion, and failure when the debug endpoint is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/samples/rxdebug_conns.c -->
