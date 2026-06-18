<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/ConditionException.h -->
## sources/distributed-fs/beegfs/common/source/common/threading/ConditionException.h

Purpose: Defines the named exception type for condition-variable failures.

Important APIs/types: Uses the `DECLARE_NAMEDEXCEPTION` macro to derive `ConditionException` from `SynchronizationException`.

Control flow/state/persistence: No runtime logic or state beyond exception construction and `what()` inherited from `NamedException`.

Dependencies/integration: Includes `SynchronizationException.h`. Thrown by `Condition.cpp` initialization paths.

Risks/test signals: Tests should ensure the exception name/message are preserved through catch by base type and that condition initialization failures map to this type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/ConditionException.h -->
