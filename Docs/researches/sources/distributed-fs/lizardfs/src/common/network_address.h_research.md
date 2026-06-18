<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/network_address.h -->
# sources/distributed-fs/lizardfs/src/common/network_address.h

## Purpose
Defines a compact IP/port address value with serialization, hashing, formatting, and connection exception context. The source was read completely for this report.

## Important APIs, Types, And Functions
`NetworkAddress`, comparison/equality, `toString`, `serializedSize/serialize/deserialize`, `std::hash<NetworkAddress>`, and `ChunkserverConnectionException` are visible.

## Control Flow
Formatting converts numeric IP through `ipToString` and appends `:port` only for nonzero ports. Serialization writes ip then port.

## State And Persistence Behavior
State is just `uint32_t ip` and `uint16_t port`; no persistence except serialized protocol use.

## Dependencies And Integration Points
Used throughout chunkserver connection, stats, and read-plan code.

## Risks And Edge Cases
Hash is MooseFS-derived and may collide; IP byte order must match project conventions. Exception stores a copy of the server address.

## Test Signals
`network_address_unittest.cc` covers string formatting for port/no-port/zero address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/network_address.h -->
