# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetTargetMappingsMsg.h

## Research
`GetTargetMappingsMsg.h` declares a header-only request for target-to-node mappings. It wraps `SimpleMsg` and initializes `NETMSGTYPE_GetTargetMappings`.

Control flow is a single inline initializer. State is only the inherited message header. Dependencies are `SimpleMsg.h`. Integration points are management queries used to populate the client `TargetMapper` before routing storage IO. Risks are protocol evolution adding payload fields without updating this wrapper, and caller confusion with other target-state requests. Test signals are management response pairing with `GetTargetMappingsRespMsg` and correct target mapper population.
