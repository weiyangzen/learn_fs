# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/util/TestXMLUtils.java

Purpose: validates XML-safe string mangling/unmangling for edit-log or metadata fields.

Important APIs/types/functions: `XMLUtils.mangleXmlString`, `unmangleXmlString`, `XMLUtils.UnmanglingError`, helper `testRoundTripImpl`.

Control flow: helpers mangle an input string, assert the exact encoded form, unmangle it, and assert original equality. Tests cover empty strings, plain ASCII strings, backslash escaping, forbidden control code points and surrogate code units, malformed escape sequences that must throw `UnmanglingError`, and optional entity reference encoding for ampersand, quotes, apostrophe, less-than, and greater-than.

State and persistence behavior: pure string transformations; no external state.

Dependencies and integration points: protects XML serialization/deserialization contracts used by HDFS metadata tooling.

Risks: expected strings encode exact escape format, so intentional format changes require coordinated fixture updates. Invalid sequence tests use try/fail/catch rather than `assertThrows`, but still assert the exception path.

Test signals: exact mangled output, round-trip equivalence, entity reference coverage, and malformed escape rejection.
