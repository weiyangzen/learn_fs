<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/SetMirrorBuddyGroupMsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/nodes/SetMirrorBuddyGroupMsgEx.h

Purpose: Declares the SetMirrorBuddyGroupMsgEx server-side message extension: management handler that registers or updates mirror buddy groups.

Important APIs/types/functions: Declarations/types: class SetMirrorBuddyGroupMsgEx : public SetMirrorBuddyGroupMsg.

Control flow: The header exposes a narrow processIncoming() override; dispatch is supplied by NetMessageFactory and the implementation builds the response synchronously.

State and persistence behavior: does not define standalone persistence; state lives in App-owned services and common message payloads.

Dependencies and integration points: Direct includes: <common/net/message/nodes/SetMirrorBuddyGroupMsg.h>.

Risks and test signals: Regression tests should cover success, missing-entry/error responses, malformed or stale message fields, and buddy-mirror behavior when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/nodes/SetMirrorBuddyGroupMsgEx.h -->
