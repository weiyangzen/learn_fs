<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/NetworkInterfaceCard.h -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/NetworkInterfaceCard.h

### Purpose
`NetworkInterfaceCard.h` defines NIC address data structures, serialization, list types, preference helpers, and the interface-discovery API.

### Important APIs, Types, And Functions
`NicAddrType` distinguishes standard TCP and RDMA NICs. `NicAddress` stores `IPAddress`, NIC type, interface name, and protocol version, with custom serializer/deserializer that preserves IPv4/IPv6 payloads and fixed-size names. `NicAddressList` is a list wrapper. `serdesNicAddressList()` provides backed-pointer serialization. `NetworkInterfaceCard` declares discovery, formatting, RDMA capability, and sorting helpers.

### Control Flow
NIC list deserialization reads serialized length/count, deserializes each `NicAddress`, and redirects the pointer to backing storage. `NicAddress::serialize()` writes protocol first, then either IPv4 or 16-byte IPv6 address, fixed name, type, and padding.

### State, Persistence, And Dependencies
State is value/list data exchanged over the wire in node descriptions. Dependencies include `IPAddress`, BeeGFS serialization, and system `IFNAMSIZ`.

### Integration Points
Node serialization, connection pools, route matching, and management node stores rely on `NicAddressList`.

### Risks
The deserializer reads `nicListLength` but does not validate it against count in this helper. Protocol values other than `4` are treated as IPv6. Tests should cover IPv4/IPv6 NIC serialization, fixed-name truncation/null termination, RDMA type preservation, and list length/count mismatch handling by the broader serialization layer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/NetworkInterfaceCard.h -->
