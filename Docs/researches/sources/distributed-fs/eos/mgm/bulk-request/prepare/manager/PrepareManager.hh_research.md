## sources/distributed-fs/eos/mgm/bulk-request/prepare/manager/PrepareManager.hh

Purpose: declares the base manager for prepare operations and query-prepare operations. It exposes public entry points and protected template hooks used by `BulkRequestPrepareManager`.

Important APIs/types: `enum PrepareAction { STAGE, EVICT, ABORT }`, overloads of `prepare()` and `queryPrepare()` for client or pre-mapped VID, hooks `initializeStagePrepareRequest()`, `initializeCancelPrepareRequest()`, `ignorePrepareFailures()`, `setErrorToBulkRequest()`, `saveBulkRequest()`, `addFileToBulkRequest()`, helpers `getPrepareActionsFromOpts()`, `isStagePrepare()`, `triggerPrepareWorkflow()`, and implementation methods `doPrepare()`/`doQueryPrepare()`.

State/integration: `mEpname`, `mPrepareAction`, and `unique_ptr<IMgmFileSystemInterface>`. Risks include `mPrepareAction` requiring initialization before `isStagePrepare()`, broad protected surface, and coupling to EOS/XRootD types. Tests should exercise base behavior and subclass hook behavior separately.
