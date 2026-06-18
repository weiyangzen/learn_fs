<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/benchmark/StorageBench.h -->
## sources/distributed-fs/beegfs/common/source/common/benchmark/StorageBench.h

### Purpose
This header defines shared constants and enums for BeeGFS storage benchmark control and status reporting.

### Important APIs, Types, And Functions
It declares error code macros, `StorageBenchResultsMap` keyed by target ID with throughput values, `StorageBenchAction`, `StorageBenchType`, `StorageBenchStatus`, and `STORAGEBENCHSTATUS_IS_ACTIVE`.

### Control Flow
There is no executable control flow. The active-status macro classifies running, finishing, and stopping as active benchmark states.

### State, Persistence, And Dependencies
No local state is stored. The types define protocol/control state used by benchmark operators and messages elsewhere. Dependency is `Common.h`.

### Integration Points
Storage benchmark management messages and workers use these values to coordinate start, stop, status, cleanup, and error reporting.

### Risks
These are preprocessor constants and unscoped enums, so names are global. Numeric values may be externally visible through network messages or user output and should not change casually.

### Test Signals
Tests should verify active status classification, error propagation through benchmark messages, and compatibility of enum numeric values if serialized.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/benchmark/StorageBench.h -->
