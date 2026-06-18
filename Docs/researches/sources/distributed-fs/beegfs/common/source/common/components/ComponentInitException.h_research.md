<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/ComponentInitException.h -->
## sources/distributed-fs/beegfs/common/source/common/components/ComponentInitException.h

### Purpose
This header defines the named exception thrown when a BeeGFS component cannot initialize.

### Important APIs, Types, And Functions
`DECLARE_NAMEDEXCEPTION(ComponentInitException, "ComponentInitException")` declares the component initialization exception type.

### Control Flow
No local control flow. Constructors for listeners and other components throw this type on socket, pipe, epoll, or related initialization failures.

### State, Persistence, And Dependencies
The exception carries inherited message state only. Dependencies are `NamedException.h` and `Common.h`.

### Integration Points
`StreamListener`, `AbstractDatagramListener`, and `StatsCollector`-adjacent components include this for startup error reporting to `AbstractApp::handleComponentException` or app startup code.

### Risks
No structured component identifier is stored; messages need to include enough context.

### Test Signals
Initialization-failure tests should assert listener socket/epoll failures raise `ComponentInitException` with actionable text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/ComponentInitException.h -->
