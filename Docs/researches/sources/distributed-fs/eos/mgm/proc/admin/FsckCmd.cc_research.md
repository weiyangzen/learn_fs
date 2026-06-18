# sources/distributed-fs/eos/mgm/proc/admin/FsckCmd.cc

Purpose: Implements the protobuf-backed `fsck` admin command, including status, configuration, report generation, single-entry repair, and orphan cleanup on FST endpoints.

Important APIs/types/functions: `FsckCmd::ProcessRequest()` dispatches `FsckProto` oneof cases. `mFsckEngine->PrintOut()` returns engine state; `Config()` changes fsck settings; `Report()` renders selected tags and display modes; `RepairEntry()` repairs a fid with an error fsid and async option. `CleanOrphans` builds a `/ ?fst.pcmd=clean_orphans` query and uses `gOFS->BroadcastQuery()`. Under `EOS_GRPC_GATEWAY`, an overload streams the same logic through `grpc::ServerWriter<ReplyProto>`.

Control flow: Non-report subcommands require `mVid.uid == 0`. Global orphan cleanup (`fsid == 0`) collects all online node hostports from `FsView::mNodeView`; per-fsid cleanup resolves the filesystem and targets its host and locator port. Broadcast failures are summarized per endpoint. The gRPC version writes the reply after each branch and has mostly duplicated control flow.

State and persistence behavior: Configuration and repair state are delegated to `mFsckEngine`. `force_qdb_cleanup` can trigger `ForceCleanQdbOrphans()` independent of disk cleanup. Orphan cleanup mutates FST-local on-disk orphan state through remote queries, not directly through MGM metadata.

Dependencies and integration points: Depends on `XrdMgmOfs`, `FsView`, and `mgm/fsck/Fsck.hh`. Integrates with online FST discovery, MGM broadcast query plumbing, and optional EOS REST/gRPC gateway generated service headers.

Risks: The gRPC and unary implementations are duplicated and can drift. Broadcast returns are treated as aggregate failure, but only endpoints with nonzero per-endpoint codes are printed. Report is allowed for non-root users, so tag and output filtering must not leak unintended data. Force QDB cleanup on global clean can run even if endpoint cleanup later fails.

Test signals: Admin authorization for every branch, non-root report access, config failure message fallback, report tag set handling, repair success/failure, global and single-fsid orphan cleanup endpoint selection, missing fsid errors, broadcast partial failures, and parity between unary and gRPC implementations.
