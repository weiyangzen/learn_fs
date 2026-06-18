# sources/distributed-fs/beegfs-go/common/beegfs/node.go

## Purpose
`node.go` defines BeeGFS node and NIC value types shared by management and CLI logic.

## APIs and Control Flow
`Node` stores UID, legacy ID, alias, and NICs. `String` returns the long legacy ID string. `Addrs` extracts NIC addresses into a new slice. `Clone` deep-copies the NIC slice before returning a node copy. `NicType` defines invalid, TCP, RDMA, and SDP variants with string output. `Nic` stores name, type, and address and formats them in a compact display string.

## State, Dependencies, and Integration
These are in-memory data models with no persistence logic. They integrate with entity ID types and user-facing output for BeeGFS nodes. The only dependency is `fmt`.

## Risks and Test Signals
The TODO notes the node should use `EntityIdSet`, indicating an identity model transition. `Clone` only deep-copies the NIC slice, which is sufficient for current scalar NIC fields. There are no listed direct tests for node cloning or formatting.
