# sources/distributed-fs/beegfs-go/watch/internal/metadata/deserialize_test.go

## Purpose

This file validates raw metadata packet decoding for known v1 and v2 BeeGFS event examples and verifies selected malformed packet errors.

## Important APIs, Types, And Functions

`TestDeserialize` defines a table of byte slices and expected `pb.Event` values. Cases include v1 unlink, v1 rename, v1 setattr with missed events, v1 close-write with dropped events, v2 create, v2 open-read, and v2 last-writer-closed. A second table checks unsupported version and mismatched v2 parsed size.

## Control Flow

Each positive case calls `deserializeEvent(tc.input, uint32(len(tc.input)))` and asserts no error plus equality with the expected protobuf. Negative cases call the same function and assert an error.

## State And Persistence

The test is pure in-memory byte decoding. It encodes protocol fixtures directly in source, making the expected wire layout visible but verbose.

## Dependencies And Integration Points

It depends on generated `beewatch` protobuf enums and testify assertions. The fixtures protect the contract consumed by `metadata.Manager` and the test file event logger utility.

## Risks And Test Signals

The tests are strong regression signals for field offsets and enum mapping, especially the v2 timestamp/user fields. They do not cover packet truncation panic paths, invalid v1 minor version, target path edge cases beyond rename, or v2 stream wrapper parsing in `serde.go`. Because fixtures are hand-coded, changes to protobuf enum values or metadata packet layout require careful fixture updates.
