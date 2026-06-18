# sources/distributed-fs/beegfs/client_module/source/common/toolkit/Serialization.h

## Purpose
Declares and partially implements the custom BeeGFS serialization framework, including primitive little-endian encoders, list/vector helpers, and macros to generate serializers for structs, lists, and enums.

## Important APIs and types
Primitive inline helpers serialize and deserialize chars, bools, uint8, short/ushort, int/uint, and int64/uint64 through `SerializeCtx` and `DeserializeCtx`. Declarations cover strings, aligned strings, char arrays, NIC lists, node lists, string copy lists/vectors, UInt8/UInt16 lists/vectors, and Int64 lists/vectors. Macro families `SERDES_DEFINE_SERIALIZERS`, `SERDES_DEFINE_SERIALIZERS_SIMPLE`, `SERDES_SERIALIZE_AS`, `SERDES_DEFINE_LIST_SERIALIZERS`, and `SERDES_DEFINE_ENUM_SERIALIZERS` generate repetitive field-order serialization code.

## State, dependencies, integration
The header depends on many BeeGFS containers and node/network types plus kernel unaligned accessors. It is a central integration point for message fields that are not protobuf-based.

## Risks and test signals
Generated serializers rely on exact field order and manual cleanup expressions. `Serialization_serializeBlock` supports a sizing pass when `ctx->data == NULL`; callers must allocate the final buffer from the computed length. Tests should compile representative macro expansions, verify endian stability, run round trips for every primitive and generated struct, and exercise allocation-failure cleanup in list deserializers.
