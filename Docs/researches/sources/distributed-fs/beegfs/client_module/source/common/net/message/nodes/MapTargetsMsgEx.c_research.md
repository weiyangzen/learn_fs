# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/MapTargetsMsgEx.c

## Research
`MapTargetsMsgEx.c` implements receive-only target mapping updates pushed to the client. Deserialization reads a `TargetPoolMappingList`, a node numeric ID, and an ack ID. Processing iterates the pool mappings and maps each target ID to the provided node ID in the app `TargetMapper`, logs new mappings in debug builds, and sends an ack response when requested. The release hook frees the deserialized pool mapping list.

Control flow is list parse, map update loop, ack response, and cleanup via `NETMESSAGE_FREE`. State changes are persistent in the client target mapper; pool IDs are deserialized but not used by this client-side mapping operation. Dependencies include `App`, `TargetMapper`, `Types.h` list serializers, `MsgHelperAck`, `SocketTk`, and `Common.h`. Risks are ignoring storage pool IDs, duplicate/remapped target behavior, release-hook requirements, and accepting mappings from untrusted/invalid node IDs. Test signals are management push updates changing target mapper contents and ack response behavior.
