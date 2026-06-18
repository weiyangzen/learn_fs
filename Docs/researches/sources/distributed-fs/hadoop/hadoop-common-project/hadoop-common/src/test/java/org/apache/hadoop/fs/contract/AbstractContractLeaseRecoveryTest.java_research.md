# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractLeaseRecoveryTest.java

Purpose: `AbstractContractLeaseRecoveryTest` validates the `LeaseRecoverable` interface and `LEASE_RECOVERABLE` path capability.

Important APIs and types: it uses `FileSystem`, `Path`, `LeaseRecoverable`, `CommonPathCapabilities.LEASE_RECOVERABLE`, AssertJ assertions, `ContractTestUtils.touch`, and `LambdaTestUtils.intercept`.

Control flow: `testLeaseRecovery()` touches a file, verifies the filesystem both advertises `LEASE_RECOVERABLE` for the path and implements `LeaseRecoverable`, then calls `recoverLease(path)` and `isFileClosed(path)`, expecting both to return true for a closed file. `testLeaseRecoveryFileNotExist()` uses a missing relative path and expects `FileNotFoundException` with "File does not exist" from both methods. `testLeaseRecoveryFileOnDirectory()` uses the parent directory of a method path and expects `FileNotFoundException` with "Path is not a file".

State and persistence behavior: one test creates an empty file. The tests do not leave open leases; they verify behavior against already-closed files, missing paths, and directories.

Dependencies and integration points: it bridges path capabilities and Java interface availability; an implementation must not merely declare the capability but also implement `LeaseRecoverable`.

Risks: expected exception messages are asserted, which can make compatible implementations fail on wording differences. The missing path is `new Path("notExist")`, not built through `path()`, so qualification is filesystem-dependent.

Test signals: pass indicates lease recovery can be invoked safely on closed files, reports closed status, rejects missing files and directories as files, and keeps path capability declarations consistent with implemented interfaces.
