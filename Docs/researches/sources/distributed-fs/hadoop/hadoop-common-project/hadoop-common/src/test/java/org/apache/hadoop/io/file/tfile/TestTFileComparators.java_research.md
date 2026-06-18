
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileComparators.java

Purpose: Negative tests for invalid TFile comparator specifications.

Important APIs and types: Uses `TFile.Writer` construction with comparator strings, Hadoop `FileSystem`, and JUnit `fail()`.

Control flow: Setup opens a temp output stream. Tests attempt to construct writers with an unsupported comparator name, a nonexistent `jclass`, and an existing class that is not a `RawComparator`. Each expects an exception and fails if writer construction succeeds.

State and persistence: Creates a temp path and deletes it after each test. Output stream and writer fields are mutable; `closeOutput()` exists but is unused by the tests.

Dependencies and integration points: Guards comparator-name parsing and reflection-based comparator loading in TFile writer construction.

Risks: Tests catch broad exceptions and print stack traces, so they do not assert exact exception types or messages. The output stream may remain open until filesystem cleanup.

Test signals: Ensures invalid comparator configurations are rejected early.
