<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/RandomDatum.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/RandomDatum.java

## Purpose
Test `WritableComparable` data generator used by SequenceFile, ArrayFile, SetFile, and related format tests. It creates variable-length random byte payloads with deterministic seeding support.

## Important APIs, Types, and Functions
Implements `WritableComparable<RandomDatum>`. `write()` stores an int length followed by raw bytes; `readFields()` resizes the backing array when needed and reads `length` bytes; `compareTo()` delegates to `WritableComparator.compareBytes`; `toString()` emits hex. Nested `Generator` produces key/value pairs from a `Random`, and nested `Comparator` extends `WritableComparator` to compare serialized records without object materialization.

## Control Flow and State
Instances carry `length` and `data`. Random construction uses length `10 + 10^(random float * 3)`, then fills bytes. Deserialization reuses or grows `data`, so bytes past `length` can remain but comparison and stringification use only active length. `Generator.next()` replaces both key and value each call.

## Dependencies and Integration Points
Integrates with Hadoop `Writable`, raw comparators, sorted maps, and file-format tests that need reproducible random records. The custom comparator is a performance-sensitive path for `SequenceFile.Sorter`.

## Risks and Test Signals
The main risk is stale trailing bytes influencing `hashCode()` because it hashes the full backing array while equality compares only `length` bytes; test use generally avoids variable shrink reuse in hash containers. It also casts in `equals` without type checks. Format tests signal serializer and comparator correctness by sorting and reading large generated datasets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/RandomDatum.java -->
