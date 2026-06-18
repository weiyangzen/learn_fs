<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/lookup/LookupIntentMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/lookup/LookupIntentMsgEx.h

## Purpose
Declares the lookup-intent mirrored message and its compound response state for multi-intent metadata operations.

## Important APIs, Types, and Functions
`LookupIntentResponseState` stores response flags, lookup/stat/revalidate/create/open results, stat data, file handle ID, entry info, stripe pattern, and path info. It serializes only fields selected by flags, sends `LookupIntentRespMsg`, and reports observable changes for successful create or open. `LookupIntentMsgEx` inherits `MirroredMessage<LookupIntentMsg, std::tuple<FileIDLock, ParentNameLock, FileIDLock>>`, declares lock/execution/forwarding hooks, helper operations, and cached lookup fields (`inodeData`, `entryID`, `lookupRes`, `inodeDataOutdated`, `diskEntryInfo`).

## Control Flow, State, and Persistence
The header encodes the operation contract: create/open are mirrored state changes; stat/revalidate/lookup are response enrichments. Cached fields are populated before or during lock acquisition and then consumed by execution to avoid redoing work on the primary.

## Dependencies and Integration Points
Integrates common lookup-intent messages, op counters, storage definitions, `MetaStore`, `StripePattern`, `StatData`, `PathInfo`, and `MirroredMessage`.

## Risks and Test Signals
Serializer flag ordering is critical for buddy replay and wire compatibility. Tests should cover response serialization for all flag combinations, `changesObservableState()` gating, `processSecondaryResponse()` create/open error extraction, and null or missing open pattern prevention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/lookup/LookupIntentMsgEx.h -->
