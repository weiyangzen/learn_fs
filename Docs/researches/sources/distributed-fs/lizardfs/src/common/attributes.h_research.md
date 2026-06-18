<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/attributes.h -->
# sources/distributed-fs/lizardfs/src/common/attributes.h

## Purpose

This header defines the fixed-size attribute byte array used for LizardFS file metadata transport.

## Important APIs, Types, and Functions

The only public definition is `typedef std::array<uint8_t, 35> Attributes`.

## Control Flow

There is no runtime control flow.

## State and Persistence Behavior

`Attributes` is value storage for a 35-byte metadata attribute record. Its size is part of protocol and metadata layout expectations.

## Dependencies and Integration Points

It depends on `<array>` and `<cstdint>`. Protocol, metadata, and client/server code can use this alias for packed attribute blobs.

## Risks and Edge Cases

Changing the size is an ABI/protocol change. The alias carries no field-level semantics, so callers must use matching pack/unpack logic elsewhere.

## Test Signals

Signals are compile-time size checks and protocol round trips that encode/decode file attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/attributes.h -->
