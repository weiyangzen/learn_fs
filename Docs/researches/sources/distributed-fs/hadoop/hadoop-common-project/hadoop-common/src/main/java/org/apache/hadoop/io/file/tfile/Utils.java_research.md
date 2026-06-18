<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/Utils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/Utils.java

## Purpose
`Utils` provides shared TFile utilities: compact variable-length integer encoding, nullable UTF-8 string encoding via Hadoop `Text`, a small version type, and lower/upper-bound binary-search helpers.

## Important APIs and Types
`writeVInt`, `writeVLong`, `readVInt`, and `readVLong` implement the TFile-specific signed variable-length integer format. `writeString` and `readString` serialize nullable strings as a VInt byte length followed by `Text` bytes. `Version` stores major/minor shorts, serializes to four bytes, compares versions, and considers versions compatible when majors match. Overloaded `lowerBound` and `upperBound` methods operate on comparator-backed and comparable lists.

## Control Flow
`writeVLong` emits one byte for values in `[-32, 127)`, then progressively larger encodings based on the sign-extended high byte range, falling through switch cases to choose two-, three-, four-, or fixed-length forms. `readVLong` decodes from the first byte range and reads the required trailing bytes. Binary search helpers use standard half-open `[low, high)` loops.

## State and Persistence
The class is stateless. Its encodings are persistent on-disk contracts used by TFile metadata/index and record streams, so changes would be format-breaking unless versioned.

## Dependencies and Integration Points
`TFile`, `BCFile`, and related TFile code use these methods for record lengths, index entries, metadata strings, and version compatibility. It depends only on `DataInput`, `DataOutput`, `Text`, `Comparator`, and `List`.

## Risks and Edge Cases
`readVInt` throws a runtime exception if the decoded long does not fit in an int. Corrupt first bytes can produce `IOException` or runtime internal errors. String decoding trusts the serialized length and may allocate large buffers for corrupt inputs. `Version.hashCode` shifts a signed short-derived major value, which is acceptable for equality but not a stable format hash. Binary search helpers assume sorted input according to the same comparator used for lookup.

## Test Signals
High-value tests include round trips for every integer encoding boundary, negative values, max/min int and long ranges, corrupt first-byte forms, nullable and non-ASCII strings, version compatibility/ordering, and binary searches over empty, duplicate, and boundary-key lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/Utils.java -->
