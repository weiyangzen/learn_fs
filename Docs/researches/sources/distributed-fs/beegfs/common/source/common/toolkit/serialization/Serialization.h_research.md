<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/serialization/Serialization.h -->
## sources/distributed-fs/beegfs/common/source/common/toolkit/serialization/Serialization.h

**Purpose:** Defines BeeGFS's core binary serialization framework: `Serializer`, `Deserializer`, collection support, primitive endian conversion, padding, raw string/block views, backed pointer helpers, atomic helpers, and buffer allocation.

**Important APIs/types/functions:** Traits `ListSerializationHasLength`, `MapSerializationHasLength`, `IsSerdesPrimitive`, `SerializeAs`; classes `Serializer`, `Deserializer`, `PadFieldTo`; namespace `serdes` helpers `as`, `rawString`, `stringAlign4`, `backedPtr`, `rawBlock`, `atomicAs`, and `base`; string operators; collection operators; and `serializeIntoNewBuffer`.

**Control flow:** `Serializer` can run in sizing mode with null buffer or writing mode with a buffer. It writes primitives in little-endian form, emits optional collection total length plus element count, and can mark an earlier position to patch lengths. `Deserializer` bounds-checks reads, sets bad state on overflow/format mismatch, validates collection lengths when present, and can enforce EOF with `parseEof`. Padding RAII objects align field sizes by skipping/writing zero bytes on destruction.

**State and persistence behavior:** Serialized output is a compact little-endian binary wire/storage format. Deserializer raw string/block helpers expose pointers into the input buffer, so the input buffer lifetime is part of deserialized state for those views.

**Dependencies and integration points:** Used throughout BeeGFS net messages, storage metadata, tests, and `PreallocatedFile`. It depends on `Byteswap`, `UInt128`, BeeGFS `Atomic`, and Boost traits/scoped arrays.

**Risks:** Serialization contracts are compatibility-critical; changing length fields, alignment, or primitive encodings breaks wire/on-disk compatibility. Sizing mode increments offsets even after bad state, so callers must check `good`. Raw pointer helpers can dangle if buffers are freed. Collection deserialization inserts items as it goes and can leave partial data on failure after `clear`. `serializeIntoNewBuffer` allocates based on the first sizing pass and returns `-1` on allocation or second-pass failure.

**Test signals:** `TestBitStore.cpp` exercises serializer/deserializer round trips for `BitStore`. Broader tests should cover primitives, endian conversion, collection length validation, string null terminators, raw block views, backed pointers, atomics, alignment, EOF checks, and malformed buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/toolkit/serialization/Serialization.h -->
