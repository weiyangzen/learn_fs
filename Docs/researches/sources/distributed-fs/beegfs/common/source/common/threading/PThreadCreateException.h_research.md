<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/PThreadCreateException.h -->
## sources/distributed-fs/beegfs/common/source/common/threading/PThreadCreateException.h

Purpose: Defines the named exception for pthread creation failures.

Important APIs/types: `PThreadCreateException` derives from `PThreadException` via `DECLARE_NAMEDEXCEPTION`.

Control flow/state/persistence: No logic beyond exception construction and inherited `what()`.

Dependencies/integration: Thrown by `PThread::start` and `PThread::startOnNumaNode` when pthread creation or attribute setup fails.

Risks/test signals: Tests should catch it as both `PThreadCreateException` and `PThreadException`, and validate messages include underlying system errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/threading/PThreadCreateException.h -->
