<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/acl_type.h -->
# sources/distributed-fs/lizardfs/src/common/acl_type.h

## Purpose

This header defines the ACL namespace/type enum used in metadata and serialization.

## Important APIs, Types, and Functions

`enum class AclType : uint8_t` has `kAccess`, `kDefault`, and `kRichACL`. Helpers are `hashCombineRaw()`, `serializedSize()`, `serialize()`, and `deserialize()`.

## Control Flow

Serialization writes the enum as one byte. Deserialization reads a byte and switches only over known values, throwing `IncorrectDeserializationException` for malformed values.

## State and Persistence Behavior

The enum value is serialized into metadata/protocol buffers wherever ACL type needs persistence.

## Dependencies and Integration Points

It depends on hash and serialization helpers and is used by ACL-bearing metadata structures.

## Risks and Edge Cases

Adding enum values requires updating `deserialize()` or old readers will reject them. The hash helper maps through `uint64_t`, so enum numeric stability matters for hashed structures.

## Test Signals

Useful signals are serialization round trips for all values and rejection of unknown byte values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/acl_type.h -->
