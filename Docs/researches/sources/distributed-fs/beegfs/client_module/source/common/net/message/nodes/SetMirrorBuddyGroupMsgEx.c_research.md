# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/SetMirrorBuddyGroupMsgEx.c

## Research
`SetMirrorBuddyGroupMsgEx.c` implements receive-only processing for mirror buddy group updates. Deserialization reads node type, primary target ID, secondary target ID, buddy group ID, allow-update boolean, and ack ID. Processing chooses the storage or metadata buddy group mapper, passes the storage target mapper when needed, calls `MirrorBuddyGroupMapper_addGroup`, logs success or detailed failure, and responds to ack requests.

Control flow rejects invalid node types by returning false before ack. State changes are persistent in metadata or storage mirror buddy group mapper state. Dependencies include `App`, `MirrorBuddyGroupMapper`, `TargetMapper`, `MsgHelperAck`, `FhgfsOpsErr`, and serialization helpers. Risks include invalid node type skipping ack, target IDs not yet mapped, update policy mistakes with `allowUpdate`, and no serialization support. Test signals are management buddy-group push updates, mapper contents after add/update, expected error logging, and ack responses.
