<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/GetQuotaInfo.h -->
## sources/distributed-fs/beegfs/common/source/common/storage/quota/GetQuotaInfo.h

Purpose: Declares the quota collection coordinator class.

Important APIs/types: `GetQuotaInfo` owns a `GetQuotaInfoConfig` and exposes `requestQuotaLimitsAndCollectResponses` and `requestQuotaDataAndCollectResponses`. Protected helpers are `getMaxMessageCount` and `calculateQuotaSums`.

Control flow/state/persistence: Instances are lightweight and store only request configuration. Actual asynchronous flow is in the implementation and delegated work items.

Dependencies/integration: Pulls in node stores, work queues, target mappers, quota data maps, and quota config. It provides a shared API for components that need current quota limits or usage.

Risks/test signals: Because the class stores config by value, tests should verify later caller-side mutations do not affect an existing object. Public methods accept many raw pointers; nullability expectations should be covered in integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/GetQuotaInfo.h -->
