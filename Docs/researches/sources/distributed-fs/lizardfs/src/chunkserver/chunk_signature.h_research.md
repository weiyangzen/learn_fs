# sources/distributed-fs/lizardfs/src/chunkserver/chunk_signature.h

## Purpose
`chunk_signature.h` declares the chunk signature value object used to read and write chunk header identity.

## Important APIs, Types, And Functions
- Static offsets and sizes define signature id, chunk id, version, chunk type, and total fixed signature size.
- Constructors support read-then-initialize and direct serialization.
- `readFromDescriptor` initializes from a file descriptor and offset.
- Accessors expose validity, chunk id, version, and type.
- `serializedSize` and `serialize` integrate with repository serialization helpers.
- Static signature id arrays document MooseFS, LizardFS 1.0, and LizardFS 1.1 ids.

## Control Flow
Typical scan flow constructs a default object, calls `readFromDescriptor`, checks return and validity, then compares id/version/type to filename or expected metadata. Write flow constructs from values and serializes.

## State And Persistence
Object fields store persisted signature data. The fixed offsets define on-disk header compatibility.

## Dependencies And Integration Points
It includes `ChunkPartType` and serialization macros. The tests use it with temporary files and serialization helpers.

## Risks
Changing `kSignatureSize`, offset constants, or `ChunkPartType` size breaks compatibility with existing chunk files unless migration logic is added.

## Test Signals
The matching unittest asserts the 22-byte serialized current size and exact byte layout.
