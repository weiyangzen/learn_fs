<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/moosefs_string.h -->
# sources/distributed-fs/lizardfs/src/common/moosefs_string.h

## Purpose
Implements MooseFS-compatible length-prefixed string serialization without NUL termination. The source was read completely for this report.

## Important APIs, Types, And Functions
`MooseFsString<LengthType>` inherits `std::string` and provides `maxLength`, `serializedSize`, `serialize`, and `deserialize`.

## Control Flow
Serialize writes length as `LengthType`, copies raw bytes, and advances the destination pointer. Deserialize reads length, checks remaining bytes, asserts the target is empty, assigns bytes, and advances source/count.

## State And Persistence Behavior
State is the inherited string content. Persistence is the serialized length+bytes format.

## Dependencies And Integration Points
Depends on `serialization.h`; used in legacy protocol/metadata compatibility.

## Risks And Edge Cases
Inheritance from `std::string` is pragmatic but can surprise users. Deserialize asserts empty output, so reusing objects without clearing aborts in debug/throw builds.

## Test Signals
`moosefs_string_unittest.cc` covers 8/16/32-bit lengths and max-length behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/moosefs_string.h -->
