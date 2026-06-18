# sources/distributed-fs/lizardfs/src/protocol/cstocl.h

## Purpose
Defines typed serializers/deserializers for chunkserver-to-client read/write response packets.

## Important APIs, Types, And Functions
`readData` serializes/deserializes read-data prefixes and defines modern and legacy prefix sizes. `readStatus` serializes chunk id plus status. `writeStatus` serializes chunk id, write id, and status.

## Control Flow
Read-data prefix serialization reserves CRC plus data bytes as extra payload, then writes version, chunk id, read offset, and read size. Prefix deserialization also extracts CRC. Status serializers use version 0 packet bodies with direct field unpacking.

## State And Persistence Behavior
No state. These wrappers define wire responses used by clients after chunkserver reads/writes.

## Dependencies And Integration Points
Depends on serialization macros, packet helpers, and IDs from `MFSCommunication.h`. Used by read/write data paths and chunkserver/client protocol handlers.

## Risks And Edge Cases
Callers must append/consume CRC and data consistently with prefix sizes. Legacy prefix size omits the version field, so compatibility code must know which format it is parsing. Status values are raw `uint8_t` LizardFS statuses and need correct higher-level error mapping.

## Test Signals
No direct `cstocl` unit test in subset; coverage should mirror `cltocs_unittest` with read data/status and write status round trips.
