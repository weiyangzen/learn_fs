# sources/distributed-fs/lizardfs/src/protocol/cltocs_unittest.cc

## Purpose
Validates client-to-chunkserver packet serialization wrappers.

## Important APIs, Types, And Functions
Defines GoogleTests for `cltocs::read`, `writeInit`, `writeData`, `writeEnd`, and `testChunk`. Uses `verifyHeader`, `verifyHeaderInPrefix`, `removeHeaderInPlace`, in/out pair macros, and chunk type constants.

## Control Flow
Each test serializes representative fields into a byte vector, verifies the command header, removes the header, deserializes the body/prefix, and asserts all output fields match input.

## State And Persistence Behavior
No persistence. Tests operate on in-memory vectors.

## Dependencies And Integration Points
Depends on `protocol/cltocs.h`, GoogleTest, `common/lizardfs_version.h`, and unittest helper headers. Protects packet wrappers used by mount/chunkserver communication.

## Risks And Edge Cases
Tests cover one modern EC-style chunk type path but do not exhaust legacy overloads, malformed versions, truncated buffers, or payload data after write/read prefixes.

## Test Signals
Passing tests signal that selected CLTOCS packet IDs, field order, versions, and prefix-size calculations remain compatible.
