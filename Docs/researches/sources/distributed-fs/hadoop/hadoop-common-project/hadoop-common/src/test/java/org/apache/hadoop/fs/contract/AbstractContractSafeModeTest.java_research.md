# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractSafeModeTest.java

Purpose: `AbstractContractSafeModeTest` validates the `SafeMode` interface on filesystems that include safe mode controls.

Important APIs and types: it uses `FileSystem`, `SafeMode`, `SafeModeAction`, and AssertJ. The private helper `verifyAndGetSafeModeInstance(FileSystem)` asserts the filesystem implements `SafeMode` and casts it.

Control flow: `testSafeMode()` obtains the test filesystem, verifies interface support, then calls `setSafeMode(GET)`, `ENTER`, `GET`, `LEAVE`, and `FORCE_EXIT`. It expects initial `GET` false, `ENTER` true, subsequent `GET` true, `LEAVE` false, and `FORCE_EXIT` false.

State and persistence behavior: the test mutates filesystem safe mode state and must return it to off through `LEAVE` and `FORCE_EXIT`. It does not create files or directories.

Dependencies and integration points: it checks interface implementation rather than path capability or contract feature flags. Concrete tests should include it only for filesystems where safe mode is supported and safe to toggle in tests.

Risks: there is no `try/finally` around safe mode transitions, so an assertion failure after `ENTER` could leave safe mode enabled until teardown or external cleanup. The assertion description uses `SafeMode.class.getClass()` in the message, which prints `Class` rather than the interface class, but does not affect behavior.

Test signals: pass indicates the filesystem implements `SafeMode` and its state transitions return the expected boolean state for get, enter, leave, and force-exit actions.
