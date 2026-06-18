<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/Condition.h -->
## sources/distributed-fs/beegfs/common/source/common/threading/Condition.h

Purpose: Wraps `pthread_cond_t` with BeeGFS mutex and timeout conventions.

Important APIs/types: `Condition` constructs with static `condAttr`, exposes `timedwait`, `signal`, `broadcast`, and indefinite `wait`. Static helpers initialize/destroy/test the condition clock.

Control flow/state/persistence: `timedwait` builds an absolute timeout using `Time::getClockVal` and treats `ETIMEDOUT` as non-exceptional. Other pthread errors throw `MutexException`. State is only the pthread condition variable.

Dependencies/integration: Used by `PThread`, `SyncCandidateStore`, `AcknowledgmentStore`, and many wait/notify paths with the custom `Mutex` wrapper.

Risks/test signals: Callers must hold the matching mutex. Tests should check timed timeout, signal/broadcast wakeups, spurious-wakeup caller loops, and behavior before static attr initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/Condition.h -->
