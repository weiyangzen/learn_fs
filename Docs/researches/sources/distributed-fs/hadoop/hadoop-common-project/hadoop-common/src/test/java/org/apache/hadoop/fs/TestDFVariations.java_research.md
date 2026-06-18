## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestDFVariations.java

Purpose: exercises `DF` parsing, mount/filesystem extraction, invalid-path handling, and current-directory mount resolution across Unix and Windows. It protects Hadoop's wrapper around the platform `df` command from malformed output and authority/mount assumptions.

Important APIs/types/functions: `DF`, overridden `DF.getExecString`, `DF.parseExecResult`, `DF.parseOutput`, `DF.getMount`, `DF.getFilesystem`, `Shell.WINDOWS`, and `GenericTestUtils.assertExceptionContains`. The inner `XXDF` class injects deterministic `df` output with a header-like ignored line and one filesystem row.

Control flow: setup creates a test root and teardown makes it writable before deleting it. `testMount` and `testFileSystem` compare parsed values, with Windows expecting drive-prefix behavior. `testDFInvalidPath` generates a non-existent random path and expects `FileNotFoundException`. `testDFMalformedOutput` feeds valid, missing, empty, and short-field outputs into parser methods. `testGetMountCurrentDirectory` resolves the canonical working directory and validates that the returned mount exists and encloses it.

State and persistence: uses only local temporary directories and in-memory `StringReader` output for parser tests. Permission reset in teardown handles tests that may alter directory writability.

Dependencies/integration points: integrates with Hadoop `Shell` platform checks, Java `File` canonical paths, and the `DF` command parser used by disk-space reporting.

Risks and test signals: vulnerable to platform-specific mount formatting and filesystem root behavior. Timeout annotations catch hangs in shell execution or parser loops. Expected failures are precise message checks for malformed `df` output.
