<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/config/ICommonConfig.h -->
## sources/distributed-fs/beegfs/common/source/common/app/config/ICommonConfig.h

### Purpose
`ICommonConfig.h` defines the shared configuration interface and storage fields used by BeeGFS common components.

### Important APIs, Types, And Functions
It stores logging settings, service ports and port shift, RDMA/TCP/UDP connection settings, buffer sizes, authentication fields, network filter files, routing restrictions, IPv6 flag, messaging and RDMA timeouts, management host, state update interval, and test connection rejection rate. It exposes getters that apply port shift and setters for the rejection rate.

### Control Flow
Most methods are simple accessors. Port getters return zero when the base port is zero, otherwise add `connPortShift`.

### State, Persistence, And Dependencies
Concrete config classes populate the protected fields during startup. These values are process configuration state consumed by listeners, connection pools, logging, and management code. Dependencies are `Common` and `InvalidConfigException`.

### Integration Points
`AbstractApp::getCommonConfig` exposes this interface to `StreamListener`, `AbstractDatagramListener`, RDMA socket setup, logger creation, and other common components.

### Risks
Fields are protected and mutable by subclasses; invariants depend on `AbstractConfig::applyConfigMap`. `connectionRejectionRate` is test-oriented but visible in the common config interface.

### Test Signals
Tests should check port shift behavior, getter defaults after `AbstractConfig` parsing, RDMA timeout propagation, authentication hash access, and reset of rejection count when setting rejection rate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/app/config/ICommonConfig.h -->
