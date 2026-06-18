<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/MutexException.h -->
## sources/distributed-fs/beegfs/common/source/common/threading/MutexException.h

Purpose: Defines the named exception type for mutex failures.

Important APIs/types: `MutexException` is declared with `DECLARE_NAMEDEXCEPTION` and derives from `SynchronizationException`.

Control flow/state/persistence: No logic beyond exception construction inherited from the macro-generated type.

Dependencies/integration: Included by mutex/condition/RW-lock wrappers when pthread errors need to become BeeGFS exceptions.

Risks/test signals: Test catch behavior through `SynchronizationException` and message preservation for representative pthread error strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/MutexException.h -->
