<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/GetTargetMappingsMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/GetTargetMappingsMsgEx.h

Purpose: Declares the GetTargetMappingsMsgEx server-side message extension: target-to-storage-node mapping query handler.

Important APIs/types/functions: Declarations/types: class GetTargetMappingsMsgEx : public GetTargetMappingsMsg.

Control flow: The header exposes a narrow processIncoming() override; dispatch is supplied by NetMessageFactory and the implementation builds the response synchronously.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/nodes/GetTargetMappingsMsg.h>.

Risks and test signals: Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/GetTargetMappingsMsgEx.h -->
