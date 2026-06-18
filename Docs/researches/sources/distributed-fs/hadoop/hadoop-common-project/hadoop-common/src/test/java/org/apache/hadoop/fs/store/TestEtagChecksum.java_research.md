# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/store/TestEtagChecksum.java

Purpose: Tests equality and Hadoop Writable serialization for `EtagChecksum`.

Important APIs/types/functions: `EtagChecksum`, `write`, `readFields`, `DataOutputBuffer`, `DataInputBuffer`, helper `tag`, and helper `roundTrip`.

Control flow: Fixtures create two empty tags and two identical valid tags. Tests assert empty tags equal, empty tags survive round trip, valid tags equal, valid tags survive round trip, valid and empty tags differ, and different valid tags differ. `roundTrip` writes to a `DataOutputBuffer`, resets a `DataInputBuffer`, reads into a new default `EtagChecksum`, and returns it.

State/persistence: In-memory buffers only.

Dependencies/integration: Validates checksum identity used by store/object filesystems and Hadoop Writable compatibility.

Risks: Does not test null tags, hashCode, string form, or malformed serialized data.

Test signals: Equality and inequality assertions before and after Writable serialization.
