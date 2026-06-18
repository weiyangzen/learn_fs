<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/RegistrationDatagramListener.cpp -->
## sources/distributed-fs/beegfs/common/source/common/components/RegistrationDatagramListener.cpp

### Purpose
This file implements the minimal datagram listener used during registration, before full application data structures are safe for general message handling.

### Important APIs, Types, And Functions
The constructor forwards setup to `AbstractDatagramListener` with thread name `RegDGramLis`. `handleIncomingMsg` permits only `Ack`, `Heartbeat`, and `Dummy` messages and builds a `NetMessage::ResponseContext` using the sender socket and shared send buffer.

### Control Flow
On each parsed message, it finds a sender socket for the source IP. If none exists, it logs a warning and returns. Allowed message types call `processIncoming`; failures are logged. Other valid messages are logged as invalid in the current registration context.

### State, Persistence, And Dependencies
No additional state beyond the base datagram listener. The method creates temporary high-resolution stats, sender socket references, and response contexts. Dependencies include `IPAddress`, `StandardSocket`, `NetMessage`, and message type constants.

### Integration Points
Used during node/service registration to receive management heartbeats and acknowledgments without allowing broader operations to touch partially initialized app state.

### Risks
The send buffer comes from the base listener and must have been allocated by `run`. The listener intentionally drops otherwise valid messages, so startup sequencing must replace it with the full listener when ready.

### Test Signals
Tests should send heartbeat, ack, dummy, and disallowed message types; verify only allowed types call `processIncoming`, missing route/socket logs a warning, and response context uses the correct source address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/RegistrationDatagramListener.cpp -->
