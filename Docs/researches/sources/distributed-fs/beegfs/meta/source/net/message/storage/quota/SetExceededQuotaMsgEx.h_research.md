<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/quota/SetExceededQuotaMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/quota/SetExceededQuotaMsgEx.h

## Purpose
Declares the exceeded-quota update message extension.

## Important APIs, Types, and Functions
`SetExceededQuotaMsgEx` inherits `SetExceededQuotaMsg` and overrides `processIncoming()`.

## Control Flow, State, and Persistence
The header exposes a non-mirrored control message whose implementation updates quota caches.

## Dependencies and Integration Points
Includes the common quota request message and BeeGFS common types. It is sent by management-side quota propagation.

## Risks and Test Signals
Header risk is low; tests should validate implementation response codes and that message fields map correctly into quota-store updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/quota/SetExceededQuotaMsgEx.h -->
