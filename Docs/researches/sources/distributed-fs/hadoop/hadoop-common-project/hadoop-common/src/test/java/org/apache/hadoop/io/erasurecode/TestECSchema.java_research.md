
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/TestECSchema.java

Purpose: Tests construction and value semantics for `ECSchema`, including option-map parsing, extra options, equality, and hash-code consistency.

Important APIs and types: Uses `ECSchema.NUM_DATA_UNITS_KEY`, `NUM_PARITY_UNITS_KEY`, `CODEC_NAME_KEY`, `new ECSchema(Map)`, `new ECSchema(codec, data, parity, extraMap)`, getters, `getExtraOptions()`, `equals()`, and `hashCode()`.

Control flow: `testGoodSchema()` builds a schema from a `HashMap`, validates fields, then compares it to an equivalent constructor-based schema. `testEqualsAndHashCode()` creates schemas varying codec, data units, parity units, and extras, then checks identity copies and pairwise inequality.

State and persistence: Only local immutable schema objects are used. Extra options are copied into schema state and participate in equality.

Dependencies and integration points: Guards the schema object consumed by erasure codec options, filesystem policy definitions, and codec factories.

Risks: The test is sensitive to whether extra options are normalized or preserved. It checks inequality against another object's hash code as a negative case, which is unusual but harmless.

Test signals: Confirms constructor equivalence and stable value-object behavior under a 300-second class timeout.
