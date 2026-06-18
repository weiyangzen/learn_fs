# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/ECSchema.java

Purpose: serializable public/evolving value object describing an erasure coding schema: codec name, number of data units, number of parity units, and codec-specific extra options.

Important APIs and control flow: map constructor extracts `codec`, `numDataUnits`, and `numParityUnits`, validates positive integers, removes those entries from the provided map, and stores remaining options as unmodifiable extras. Direct constructors accept key parameters and optional extras. Getters expose fields; `toString()`, `equals()`, and `hashCode()` include all fields including extras.

State and persistence: immutable final fields plus unmodifiable map; serializable with fixed `serialVersionUID`. The map constructor mutates its input map while stripping core keys.

Dependencies and integration: used by `ErasureCodecOptions`, codec creation, `BlockGrouper`, and EC policy handling outside this subset.

Risks and test signals: test validation messages, input-map mutation, equality/hash with extra options, and serialization compatibility. Direct constructors rely on assertions for validation, so production callers should validate before construction.
