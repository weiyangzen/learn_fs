<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/Channel.h -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/Channel.h

### Purpose
`Channel` is the common pollable communication endpoint base, storing connection classification, activity, authentication, and peer node identity metadata.

### Important APIs, Types, And Functions
It derives from `Pollable`. State fields are `isDirect`, `hasActivity`, `isAuthenticated`, `NodeType nodeType`, and `NumNodeID nodeID`. Inline getters/setters expose direct-work status, idle/activity tracking, authentication, node type, and node ID.

### Control Flow
The protected constructor initializes channels as direct, active, unauthenticated, and with invalid node type. Worker/connection handling code toggles activity and authentication as messages are received.

### State, Persistence, And Dependencies
State is in-memory per connection and not persisted. It depends on `Pollable`, `NodeType`, and `NumNodeID`.

### Integration Points
`Socket` derives from `Channel`, so TCP/RDMA sockets inherit these flags. Worker pools and authentication handlers use them to manage routing and idle disconnects.

### Risks
The booleans are not internally synchronized; callers must respect owning-thread or external-lock assumptions. Tests should cover initial state, authentication transitions, activity reset/set behavior, and propagation through socket subclasses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/Channel.h -->
