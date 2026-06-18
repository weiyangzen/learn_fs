# sources/distributed-fs/beegfs/client_module/source/common/toolkit/SerializationTypes.h

## Purpose
Defines the minimal context structs used by the BeeGFS serialization layer.

## Important APIs and types
`SerializeCtx` contains a constant output data pointer and a running `length`. When `data` is `NULL`, serializers still advance `length` for sizing. `DeserializeCtx` contains a current data pointer and remaining length. `RawList` records a raw list payload pointer, byte length, and element count after preprocess.

## State, dependencies, integration
These structs carry transient cursor state only. They are used by `Serialization.c`, `Serialization.h` inline helpers, and generated serdes macros throughout network message code.

## Risks and test signals
The context structs do not carry capacity separately from length and rely on callers to provide valid buffers. Tests should assert that deserializers reduce `length` and advance `data` consistently, and that sizing and writing passes produce identical final lengths.
