# sources/distributed-fs/beegfs/client_module/source/common/toolkit/Serialization.c

## Purpose
Implements BeeGFS client-module wire serialization/deserialization helpers for strings, raw arrays, NIC lists, node lists, string lists/vectors, and integer list/vector containers.

## Important APIs and control flow
`__Serialization_deserializeNestedField` consumes a length-prefixed nested field and exposes a bounded inner context. String helpers serialize length, bytes, and terminating zero, with an aligned variant adding padding to a 4-byte boundary. NIC list serialization writes total length, count, protocol marker, address bytes, fixed-size name, NIC type, and padding; preprocess validates and slices raw list data. Node list preprocess walks variable fields to validate a buffer, while `Serialization_deserializeNodeList` constructs `Node` objects using app RDMA NIC context. List/vector serializers write total byte length and count, then payload elements; preprocess functions validate lengths before callers append decoded values.

## State, dependencies, integration
Serialization state is held in caller-provided `SerializeCtx`, `DeserializeCtx`, and `RawList`. The file depends on unaligned little-endian accessors, `NicAddressList`, BeeGFS list/vector wrappers, `Node_construct`, `App_lockNicList`, and Linux list/container helpers. It is used by network message implementations across the client.

## Risks and test signals
`__Serialization_deserializeNestedField` subtracts the header length from an unsigned length; malformed lengths below four can underflow. Node deserialization uses `.length = -1` for its inner context after preprocess, relying on prior validation. Tests should fuzz truncated buffers, invalid terminators, nested length underflow, invalid NIC protocols, large element counts, and compatibility between list and vector wire formats.
