# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetStatesAndBuddyGroupsMsg.h

## Research
`GetStatesAndBuddyGroupsMsg.h` declares a concrete `NetMessage` for requesting target states and buddy group mappings. The structure stores `NodeType nodeType` and `NumNodeID requestedByClientID`, and the inline initializer sets `NETMSGTYPE_GetStatesAndBuddyGroups` with the corresponding ops.

Control flow is initialization plus serializer/deserializer in the `.c` file. State is fixed-size and non-owning. Dependencies include `NetMessage.h`, `NumNodeID.h`, and `Node.h`. Integration points are internode syncer and management communication code that refreshes target states and mirror buddy groups. Risks are invalid enum values and synchronization requirements with response list types in `Types.h`. Test signals are management query success for metadata/storage states and correct local client ID propagation.
