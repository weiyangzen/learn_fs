<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/parselog.cc -->
# sources/distributed-fs/coda/coda-src/resolution/parselog.cc

Purpose: parses serialized remote resolution logs shipped by a coordinator into host- and vnode-indexed in-memory lists.

Important APIs/control flow: `ParseRemoteLogs` calls `ReadOpsFromBuf` to allocate an array of `rsle` records and initialize each from a dumped `recle` buffer. It then builds an `olist` of `he` host entries; within each host it groups entries into `remoteloglist` objects keyed by directory vnode/unique. `DeallocateRemoteLogs` frees host/list wrapper structures. `FindLogList` and `FindRemoteLog` retrieve a vnode-specific remote log.

State/persistence: parsed `rsle` records live in one allocated array returned via `RemoteLogEntries`; host/vnode lists hold pointers into that array. The wrapper lists are transient and must not outlive the array.

Dependencies/integration: depends on `rsle::InitFromRecleBuf`, `resutil::he`, `remoteloglist`, `ThisHostAddr`, and Coda list containers. Output is consumed by `compops.cc`, rename/RU conflict detection, and directory resolution.

Risks/test signals: assumes serialized entries are ordered by host because a host change creates a new `he` without searching for existing hosts. Corrupt buffer sizes rely on assertions, not graceful errors. Test with multi-host/multi-vnode logs, zero entries, unsorted host entries, and malformed/truncated dump buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/coda/coda-src/resolution/parselog.cc -->
