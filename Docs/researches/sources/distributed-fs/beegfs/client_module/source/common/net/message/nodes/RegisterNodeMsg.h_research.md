# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/RegisterNodeMsg.h

## Research
`RegisterNodeMsg.h` declares the outgoing node registration message. The struct embeds `NetMessage` and stores non-owned node ID, numeric ID, root info, node type, non-owned NIC list, UDP/TCP ports, version fields, and machine UUID. `RegisterNodeMsg_initFromNodeData` fills client-relevant fields, sets root info and TCP/machine UUID to client defaults, and initializes `NETMSGTYPE_RegisterNode`.

Control flow is construction followed by serialization in the `.c` file. State is non-owning for strings and NIC list; no release hook exists. Dependencies are `NetMessage.h`, `NetworkInterfaceCard.h`, and `BitStore.h`. Integration points are registration with management and local-node identity setup. Risks include using stack/temporary alias strings or NIC lists beyond their lifetime, zero default fields being interpreted differently by servers, and no deserialization support. Test signals are startup registration success and `RegisterNodeRespMsg` carrying assigned IDs.
