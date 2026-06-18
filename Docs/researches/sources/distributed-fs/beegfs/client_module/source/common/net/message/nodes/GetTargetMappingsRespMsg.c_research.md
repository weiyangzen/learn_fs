# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetTargetMappingsRespMsg.c

## Research
`GetTargetMappingsRespMsg.c` implements receive-only deserialization and cleanup for target mapping responses. `GetTargetMappingsRespMsg_deserializePayload` reads a `TargetMappingList` into the message-owned `mappings` list, and the release hook frees every `TargetMapping` list element.

Control flow is simple but ownership-sensitive: successful or partial deserialization must be followed by `NETMESSAGE_FREE` to run the release hook. State is a list of `TargetMapping` objects allocated by the list serializer. Dependencies are `GetTargetMappingsRespMsg.h`, `Types.h` serializers, `TargetMapper.h`, and `Common.h` cleanup macros. Integration points are target mapper refresh and storage IO target routing. Risks are leaks without release, using list entries after message free, and wire compatibility of `TargetMapping`. Test signals are target ID mapping updates, malformed list rejection, and cleanup verification.
