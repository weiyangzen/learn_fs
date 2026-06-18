<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/SetTargetConsistencyStatesMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/SetTargetConsistencyStatesMsgEx.h

Purpose: Declares the SetTargetConsistencyStatesMsgEx server-side message extension: management handler that updates target consistency states in the appropriate target state store.

Important APIs/types/functions: Declarations/types: class SetTargetConsistencyStatesMsgEx : public SetTargetConsistencyStatesMsg.

Control flow: The header exposes a narrow processIncoming() override; dispatch is supplied by NetMessageFactory and the implementation builds the response synchronously.

State and persistence behavior: mutates target consistency/reachability state.

Dependencies and integration points: Direct includes: <common/net/message/nodes/SetTargetConsistencyStatesMsg.h>.

Risks and test signals: Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/SetTargetConsistencyStatesMsgEx.h -->
