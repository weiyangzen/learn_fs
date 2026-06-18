# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractCreateTest.java

Purpose: `AbstractContractCreateTest` is the main file-creation contract suite. It checks basic create, overwrite rules, directory collisions, visibility timing, block size reporting, automatic parent creation, parent-file rejection, and stream sync semantics.

Important APIs and types: it uses `FileSystem`, `Path`, `FSDataOutputStream`, `FSDataInputStream`, `FileStatus`, `FileAlreadyExistsException`, `ParentNotDirectoryException`, `StreamCapabilities`, and `TestAbortedException`. Key helpers are `writeDataset`, `writeTextFile`, `touch`, `getFileStatusEventually`, `assertCapabilities`, `validateSyncableSemantics()`, `expectCreateUnderFileFails()`, and `expectMkdirsUnderFileFails()`.

Control flow: paired helper methods run most create tests against both classic create and builder-based create paths by passing `useBuilder`. The suite writes datasets, verifies contents, attempts forbidden overwrites, checks directory preservation, waits for eventual file status, validates block sizes, creates parent trees, and probes parent-file errors. `testSyncable()` reads contract flags for `SUPPORTS_HFLUSH`, `SUPPORTS_HSYNC`, and `METADATA_UPDATED_ON_HSYNC`, then verifies stream capability declarations and actual hflush/hsync behavior.

State and persistence behavior: tests create real files and directories under method-specific contract paths. Visibility tests explicitly account for object store and delayed-visibility filesystems through `IS_BLOBSTORE` and `CREATE_VISIBILITY_DELAYED`. Sync tests write bytes before close, optionally open a separate reader during the write, and inspect metadata length when declared supported.

Dependencies and integration points: the file is tightly coupled to `ContractOptions` feature flags and `ContractTestUtils` dataset helpers. It integrates with stream capability APIs and IO statistics logging for output streams. The builder path exercises Hadoop's newer create-file builder indirectly through test utilities.

Risks: relaxed exception handling allows some implementations to pass with generic `IOException`, so precise exception conformance is not always enforced. Visibility and sync behavior are difficult for object stores and append-only backends; incorrect contract flag values can turn real bugs into skips or failures. `testOverwriteNonEmptyDirectory` contains explicit accommodation for filesystems that implement file/directory overlays.

Test signals: pass indicates create and overwrite semantics are coherent, parent directories are populated, creating under files is rejected unless explicitly supported, block sizes are plausible, visibility timing matches declared behavior, and syncable stream capabilities align with actual hflush/hsync effects.
