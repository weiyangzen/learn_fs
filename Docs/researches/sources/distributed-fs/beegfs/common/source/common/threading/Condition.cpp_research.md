<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/Condition.cpp -->
## sources/distributed-fs/beegfs/common/source/common/threading/Condition.cpp

Purpose: Implements static condition-variable attributes and safe clock validation.

Important APIs/functions: `initStaticCondAttr` initializes a global `pthread_condattr_t` and sets `SAFE_CLOCK_ID`. `destroyStaticCondAttr` destroys it. `testClockID` validates that the selected monotonic/realtime clock works and advances.

Control flow/state/persistence: Static initialization configures all `Condition` instances to use the safe clock. Errors throw `ConditionException`, `MutexException`, or `TimeException`. No persistence exists.

Dependencies/integration: Uses `System::getErrString`, `Time`, BeeGFS exceptions, and pthread condition attributes. `Condition.h` depends on this static attr for constructor behavior.

Risks/test signals: Process initialization order matters. Tests should cover attr initialization/destroy, clock failures through mocks, and timed wait consistency with the configured clock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/Condition.cpp -->
