# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/shell/TestPrintableString.java

Purpose: Verifies `PrintableString` sanitizes strings for shell display by retaining printable Unicode and replacing non-printable, private-use, unassigned, and invalid surrogate code points with `?`.

Important APIs/types/functions: `PrintableString.toString`, AssertJ assertions, helper `expect(reason, raw, expected)`.

Control flow: `testPrintableCharacters` feeds ASCII, BMP Unicode, and supplementary-plane surrogate pairs and expects exact preservation. `testNonPrintableCharacters` feeds control characters, Unicode formatting characters, private-use characters across BMP and supplementary planes, unassigned code points, and standalone surrogate cases, expecting `?` replacement while valid characters remain.

State/persistence: No external state. Each assertion constructs a new `PrintableString`.

Dependencies/integration: Exercises Java Unicode category handling through the shell string display helper. This protects FS shell output from invisible/control path characters while preserving legitimate international path names.

Risks: Behavior depends on Java Unicode tables; future JVM Unicode category updates may shift classifications for unassigned/private/formatting characters. The test uses literal surrogate pairs, so editor/encoding handling matters.

Test signals: Exact sanitized strings for representative printable, non-printable, supplementary, and malformed surrogate inputs.
