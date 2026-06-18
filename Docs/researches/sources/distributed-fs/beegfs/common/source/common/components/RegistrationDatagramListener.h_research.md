<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/RegistrationDatagramListener.h -->
## sources/distributed-fs/beegfs/common/source/common/components/RegistrationDatagramListener.h

### Purpose
This header declares the restricted datagram listener used during BeeGFS registration.

### Important APIs, Types, And Functions
`RegistrationDatagramListener` derives from `AbstractDatagramListener`, forwards construction parameters for filters, NICs, ack store, UDP port, and outbound-interface restriction, and overrides `handleIncomingMsg`.

### Control Flow
The header establishes that only incoming-message policy differs from the base listener; all socket and send behavior remains inherited.

### State, Persistence, And Dependencies
No new fields are declared. Dependencies include `IPAddress`, `AbstractDatagramListener`, and `Common`.

### Integration Points
Registration code can instantiate this class where a full datagram listener would be unsafe before local node/app state is complete.

### Risks
The minimal class relies on comments and implementation to enforce allowed message types; future additions should avoid broadening startup behavior accidentally.

### Test Signals
Compile-time and runtime tests should ensure construction succeeds with the same inputs as the base and dispatch remains restricted to registration-safe message types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/RegistrationDatagramListener.h -->
