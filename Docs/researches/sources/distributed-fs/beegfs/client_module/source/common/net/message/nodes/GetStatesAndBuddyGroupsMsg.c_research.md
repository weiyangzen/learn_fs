# sources/distributed-fs/beegfs/client_module/source/common/net/message/nodes/GetStatesAndBuddyGroupsMsg.c

## Research
`GetStatesAndBuddyGroupsMsg.c` implements the request payload for combined target states and buddy groups. It serializes `nodeType` as an int and `requestedByClientID` as a `NumNodeID`, and deserializes the same fields.

Control flow is linear, with boolean chaining on deserialize. State is fixed-size: requested node type and client numeric ID. Dependencies are `GetStatesAndBuddyGroupsMsg.h`, serialization helpers, and `NumNodeID`. Integration points are management queries that return both mirror group membership and target state information in one response, typically used by client syncers. Risks are casting `NodeType` through `int32_t*` during deserialization, invalid node type values, and relying on server/client wire-order agreement. Test signals are request construction with local client ID and correct response matching through `GetStatesAndBuddyGroupsRespMsg`.
