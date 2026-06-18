# sources/distributed-fs/beegfs/common/source/common/components/worker/GetQuotaInfoWork.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/GetQuotaInfoWork.h -->
## sources/distributed-fs/beegfs/common/source/common/components/worker/GetQuotaInfoWork.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/components/worker/GetQuotaInfoWork.h` defines or implements worker component `GetQuotaInfoWork` in the BeeGFS Work framework. More broadly, it participates in the generic BeeGFS worker framework or a concrete worker task executed by Worker threads.

### Important APIs, Types, And Functions
Important APIs/classes detected: [('GetQuotaInfoWork', 'Work')]. Runtime methods include process() for Work subclasses or thread lifecycle methods for Worker/UnixConnWorker-derived classes. Dependencies include common/Common.h, common/net/message/storage/quota/GetQuotaInfoMsg.h, common/nodes/Node.h, common/storage/quota/Quota.h, common/storage/quota/QuotaData.h, common/storage/quota/GetQuotaInfo.h, common/toolkit/SynchronizedCounter.h, Work.h. Detected classes are [('GetQuotaInfoWork', 'Work')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow follows the Work contract: Worker supplies reusable buffers, process() performs the task, records stats or completion counters, and the queue/worker owns deletion after processing.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/Common.h`, `common/net/message/storage/quota/GetQuotaInfoMsg.h`, `common/nodes/Node.h`, `common/storage/quota/Quota.h`, `common/storage/quota/QuotaData.h`, `common/storage/quota/GetQuotaInfo.h`, `common/toolkit/SynchronizedCounter.h`, `Work.h`. Important local state or payload members include `GetQuotaInfoConfig cfg;       // configuration qith all information to query the quota data`, `NodeHandle storageNode;       // the node query`, `int messageNumber;            // the message number which is processed by this work`, `QuotaDataMap* quotaResults;   // the quota data from the server after requesting the server`, `QuotaInodeSupport* quotaInodeSupport;  // the support level for inode quota of the blockdevice`, `Mutex* quotaResultsMutex;     // synchronize quotaResults and quotaInodeSupport`, `SynchronizedCounter* counter; // counter for finished worker`, `uint16_t* result;             // result of the worker, 0 if success, if error the TargetNumID`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include thread synchronization, wakeup, and exactly-once completion semantics. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include success, invalid input, and error/exception paths through process methods, enqueue/dequeue ordering, worker deletion, stats/counter updates, and shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/GetQuotaInfoWork.h -->
