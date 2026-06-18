<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/GetHighResStatsMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/GetHighResStatsMsgEx.h

Purpose: Declares the GetHighResStatsMsgEx server-side message extension: statistics query handler for high-resolution metadata server operation counters.

Important APIs/types/functions: Declarations/types: class GetHighResStatsMsgEx : public GetHighResStatsMsg.

Control flow: The header exposes a narrow processIncoming() override; dispatch is supplied by NetMessageFactory and the implementation builds the response synchronously.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/storage/StorageErrors.h>, <common/net/message/storage/GetHighResStatsMsg.h>.

Risks and test signals: Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/GetHighResStatsMsgEx.h -->
