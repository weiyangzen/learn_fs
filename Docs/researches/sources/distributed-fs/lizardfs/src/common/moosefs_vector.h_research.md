<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/moosefs_vector.h -->
# sources/distributed-fs/lizardfs/src/common/moosefs_vector.h

## Purpose
Implements MooseFS-compatible vector serialization that omits an explicit element count. The source was read completely for this report.

## Important APIs, Types, And Functions
`MooseFSVector<T>` inherits `std::vector<T>` and defines `serializedSize`, `serialize`, and `deserialize`.

## Control Flow
Serialize writes each element in sequence. Deserialize repeatedly appends default elements and deserializes until the supplied byte count reaches zero.

## State And Persistence Behavior
State is inherited vector contents. Persisted form is concatenated element encodings with length known externally.

## Dependencies And Integration Points
Depends on `serialization.h`; used for legacy protocol structures where array size is implied by packet size.

## Risks And Edge Cases
Malformed element encodings can leave a partially appended default element if deserialization throws. The assertion requiring bytes to decrease protects infinite loops but only under assertions.

## Test Signals
`moosefs_vector_unittest.cc` checks std::vector-like behavior and serialization round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/moosefs_vector.h -->
