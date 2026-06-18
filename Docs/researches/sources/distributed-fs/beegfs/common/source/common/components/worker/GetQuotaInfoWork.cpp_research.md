# sources/distributed-fs/beegfs/common/source/common/components/worker/GetQuotaInfoWork.cpp

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/GetQuotaInfoWork.cpp -->
## sources/distributed-fs/beegfs/common/source/common/components/worker/GetQuotaInfoWork.cpp

### Purpose
`sources/distributed-fs/beegfs/common/source/common/components/worker/GetQuotaInfoWork.cpp` implements worker-side quota retrieval and aggregation for storage quota queries. More broadly, it participates in the generic BeeGFS worker framework or a concrete worker task executed by Worker threads.

### Important APIs, Types, And Functions
process() creates GetQuotaInfoMsg, prepareMessage() sets target-selection and ID-list/range/single-ID query mode, requestResponse() fetches GetQuotaInfoRespMsg, mergeOrInsertNewQuotaData() merges QuotaData into a shared QuotaDataMap under quotaResultsMutex, and mergeQuotaInodeSupportUnlocked() combines support states. Every completion increments a SynchronizedCounter and updates result on failures. Detected classes are none; structs none; enums none; notable out-of-line methods ['GetQuotaInfoWork::getIDRangeForMessage()', 'GetQuotaInfoWork::getIDsFromListForMessage()', 'GetQuotaInfoWork::mergeOrInsertNewQuotaData()', 'GetQuotaInfoWork::mergeQuotaInodeSupportUnlocked()', 'GetQuotaInfoWork::prepareMessage()', 'GetQuotaInfoWork::process()'].

### Control Flow
State is borrowed shared quota results, quotaInodeSupport, mutex, counter, result pointer, cfg, storageNode, messageNumber, and storagePoolId. Dependencies include GetQuotaInfoMsg/Resp, MessagingTk, QuotaData, NodeHandle, Mutex, and StringTk.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `GetQuotaInfoWork.h`, `common/net/message/storage/quota/GetQuotaInfoRespMsg.h`, `common/toolkit/MessagingTk.h`, `mutex`. Important local state or payload members include `GetQuotaInfoRespMsg* respMsgCast`, `unsigned startRange, endRange`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_GetQuotaInfoResp`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include thread synchronization, wakeup, and exactly-once completion semantics, message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, success, invalid input, and error/exception paths through process methods, enqueue/dequeue ordering, worker deletion, stats/counter updates, and shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/worker/GetQuotaInfoWork.cpp -->
