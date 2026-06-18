# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/test/PlatformAssumptions.java

Purpose: JUnit assumption helpers for OS-specific tests.

Important APIs/types/functions: constants `OS_NAME` and `WINDOWS`; static methods `assumeNotWindows()`, `assumeNotWindows(String)`, and `assumeWindows()`.

Control flow: methods inspect `System.getProperty("os.name")`. If the platform does not match the requested assumption, they throw `TestAbortedException`, causing the JUnit test to be skipped/aborted rather than failed.

State and persistence behavior: `OS_NAME` and `WINDOWS` are static process-time values. No persistence.

Dependencies and integration points: integrates with JUnit 5/OpenTest4J's `TestAbortedException`. Used by tests that have Unix-only or Windows-only behavior.

Risks and test signals: simple `startsWith("Windows")` detection is stable for common JVMs but not a full platform abstraction. Test signal is skip behavior rather than assertion failure.
