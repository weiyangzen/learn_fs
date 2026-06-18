<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/SetLastBuddyCommOverrideMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/SetLastBuddyCommOverrideMsg.h

### Purpose
`SetLastBuddyCommOverrideMsg` asks a storage node to override the recorded last communication timestamp for a buddy target, optionally aborting a running resync so it restarts from the new timestamp state.

### Important APIs, Types, And Functions
It derives from `NetMessageSerdes<SetLastBuddyCommOverrideMsg>` with type `NETMSGTYPE_SetLastBuddyCommOverride`. Serialization writes `targetID`, `timestamp`, and `abortResync`. Getters expose all three fields.

### Control Flow
The message is constructed with all required fields, then receiver logic applies the timestamp override and abort decision.

### State, Persistence, And Dependencies
The message is transient, but it updates persistent resync timestamp state on the receiver. It depends on NetMessage serdes and storage resync policy outside this file.

### Integration Points
Management tools or recovery code use it to force resync windows for buddy targets.

### Risks
Incorrect timestamps can skip required resync work or cause excessive resync. Abort semantics must coordinate with running jobs. Tests should cover timestamp round-trip, abort true/false, unknown target IDs, and active-resync restart behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/SetLastBuddyCommOverrideMsg.h -->
