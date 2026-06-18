# sources/distributed-fs/beegfs/client_module/source/common/net/message/control/PeerInfoMsg.h

## Research
`PeerInfoMsg.h` declares a concrete `NetMessage` carrying peer node type and `NumNodeID`. `PeerInfoMsg_init` sets `NETMSGTYPE_PeerInfo`, installs `PeerInfoMsg_Ops`, and stores the caller-supplied identity fields.

Control flow is inline construction and the `.c` payload ops. State is fixed-size and owned by the message instance. Dependencies include `NetMessage.h` and `Node.h` for `NodeType` and `NumNodeID`. Integration points are connection establishment and peer classification for node connection pools. Risks are missing validation for zero node IDs or invalid node types in the header itself, and keeping the wire order synchronized with server/common implementations. Test signals are successful peer-info exchange and rejection or safe handling of invalid peer identities in higher layers.
