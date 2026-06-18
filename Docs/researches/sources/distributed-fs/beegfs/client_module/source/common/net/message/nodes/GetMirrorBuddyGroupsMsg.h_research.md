# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetMirrorBuddyGroupsMsg.h

## Research
`GetMirrorBuddyGroupsMsg.h` declares a request for mirror buddy group mappings. It is a `SimpleIntMsg` wrapper initialized with `NETMSGTYPE_GetMirrorBuddyGroups`, and the integer payload is the requested `NodeType`.

Control flow is a single inline constructor that stores the node type. State is inherited `SimpleIntMsg` state with no resources. Dependencies are `SimpleIntMsg.h` and `NodeType` visibility from included common headers. Integration points are management-node queries used to populate metadata or storage buddy group mappers. Risks are invalid node type values and no local validation of whether the requested group class supports mirroring. Test signals are successful management responses and correct mapper updates for metadata versus storage groups.
