# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractSetTimesTest.java

Purpose: `AbstractContractSetTimesTest` validates `FileSystem.setTimes(Path, mtime, atime)` behavior for missing files when the filesystem declares `SUPPORTS_SETTIMES`.

Important APIs and types: it uses `Path`, `FileNotFoundException`, JUnit, SLF4J, and the base contract methods `skipIfUnsupported()` and `handleExpectedException()`.

Control flow: `setup()` calls the base setup, skips unsupported filesystems, and initializes `testPath` and `target`. `testSetTimesNonexistentFile()` calls `setTimes()` on the missing target with current time for both modification and access time. Reaching normal completion fails the test; `FileNotFoundException` is expected.

State and persistence behavior: no file is created. The test verifies that `setTimes()` does not create missing paths as a side effect.

Dependencies and integration points: this is a focused feature-gated contract test. It depends on concrete filesystems setting `SUPPORTS_SETTIMES` only when the API is implemented.

Risks: the class only tests the negative missing-file case, not successful timestamp updates on files or directories. The logger and `testPath` field are not substantively used beyond path construction.

Test signals: pass indicates `setTimes()` on a nonexistent file fails with `FileNotFoundException` and does not silently create or ignore missing paths.
