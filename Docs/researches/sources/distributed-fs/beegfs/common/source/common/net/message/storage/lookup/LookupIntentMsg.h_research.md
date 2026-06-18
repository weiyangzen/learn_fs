<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/lookup/LookupIntentMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/lookup/LookupIntentMsg.h

### Purpose
`LookupIntentMsg` combines lookup with optional revalidate, create, exclusive-create, open, and stat intents. It is a latency-reducing metadata request that lets one network message perform a compound client operation and carries extra fields when buddy-mirror replay is involved.

### Important APIs, Types, And Functions
The class derives from `MirroredMessageBase<LookupIntentMsg>` and reports `supportsMirroring() == true`. Payload intent flags are `LOOKUPINTENTMSG_FLAG_REVALIDATE`, `CREATE`, `CREATEEXCLUSIVE`, `OPEN`, and `STAT`; header feature flags include quota/event support. Key mutators are `addIntentCreate()`, `addIntentCreateExclusive()`, `addIntentOpen()`, `addIntentStat()`, `addBuddyInfo()`, and timestamp/FD setters inherited or exposed through protected fields. Serialization conditionally includes parent info, entry name, revalidate metadata/version, open access/session data, create ownership/mode/targets, optional `FileEvent`, and buddy-mirror second-phase IDs, stripe pattern, owner FD, and timestamps.

### Control Flow
Every message starts with `intentFlags`, parent entry info, and entry name. Optional blocks are serialized only if their flags are set. When `Flag_BuddyMirrorSecond` is present, create messages include the preselected new entry ID/stripe pattern/owner FD/dir timestamps, and all buddy-second messages include file timestamps.

### State, Persistence, And Dependencies
The message is transient but carries fields that later become persistent metadata: entry IDs, stripe patterns, owner/session state, and timestamps. It depends on `EntryInfo`, `FileEvent`, `StatData`, `StripePattern`, `MirroredMessageBase`, and NetMessage header flags.

### Integration Points
Client lookup/open/create/stat paths and metadata mirroring use this message. Its flag definitions must remain synchronized with the client-mode counterpart named in the comment.

### Risks
Flag-dependent layouts are brittle: sender and receiver must agree exactly or subsequent fields shift. Optional pointers such as preferred targets, entry info, and stripe pattern are non-owned. Buddy-mirror second-phase data is security and consistency sensitive because it replays chosen IDs and timestamps. Tests should cover every flag combination, event feature flag absence/presence, buddy-secondary serialization, exclusive create, and backward compatibility with clients that lack newer header feature flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/lookup/LookupIntentMsg.h -->
