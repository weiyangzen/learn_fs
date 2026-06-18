## sources/distributed-fs/eos/mgm/bulk-request/interface/RealMgmFileSystemInterface.cc

Purpose: implements `IMgmFileSystemInterface` by forwarding calls to a concrete `XrdMgmOfs` instance and related MGM services.

Important behavior: methods delegate to `MgmStats`, `mTapeEnabled`, `mReqIdMax`, `Emsg`, `_exists`, `_attr_ls`, `_access`, `FSctl`, `_stat`, `_stat_set_flags`, `logId`, host/alias fields, and `mIoStats->WriteRecord()` when present.

State/dependencies: stores non-owning `XrdMgmOfs*`. Integration is the production adapter for `PrepareManager`. Risks include no null guard for `mMgmOfs`, fallback host string behavior, and report records being silently dropped if `mIoStats` is absent. Tests should use fake `XrdMgmOfs` only in integration-style builds; most prepare unit tests should mock the interface instead.
