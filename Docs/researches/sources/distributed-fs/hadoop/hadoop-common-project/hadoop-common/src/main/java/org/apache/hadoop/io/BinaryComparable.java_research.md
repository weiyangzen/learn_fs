<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/BinaryComparable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/BinaryComparable.java

Purpose: abstract comparable base for types whose ordering, equality, and hash code are defined by a byte prefix.

Important APIs, types, and functions: subclasses implement `getLength()` and `getBytes()`. `compareTo(BinaryComparable)` and `compareTo(byte[], off, len)` delegate to `WritableComparator.compareBytes()`. `equals()` checks type and length before comparing bytes. `hashCode()` delegates to `WritableComparator.hashBytes()`.

Control flow: callers compare the valid range `[0, getLength())` of the returned backing byte array.

State and persistence: no state in the base class; subclass backing bytes provide behavior.

Dependencies and integration points: base for byte-oriented writables such as `BytesWritable` and `Text`.

Risks and test signals: subclasses must ensure `getBytes()` has at least `getLength()` valid bytes and stable contents while used as keys. Tests should cover lexicographic ordering, equality/hash consistency, prefix differences, and mutable backing array hazards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/BinaryComparable.java -->
