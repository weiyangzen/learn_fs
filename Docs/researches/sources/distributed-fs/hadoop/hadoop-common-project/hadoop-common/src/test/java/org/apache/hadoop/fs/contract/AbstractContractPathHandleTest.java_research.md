# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractPathHandleTest.java

Purpose: `AbstractContractPathHandleTest` validates `PathHandle` creation and open semantics across different `HandleOpt` policies for content changes and path/location changes.

Important APIs and types: it uses `PathHandle`, `RawPathHandle`, `HandleOpt`, `InvalidPathHandleException`, `FileStatus`, `FSDataInputStream`, `CompletableFuture`, `FileSystem.getPathHandle()`, `FileSystem.open(PathHandle)`, and `FileSystem.openFile(PathHandle)`. It is parameterized over `exact`, `content`, `path`, and `reference` options, each with serialized and non-serialized handle use.

Control flow: `params()` creates the option matrix. `initAbstractContractPathHandleTest()` stores options and serialization mode. `testIdent()` gets a handle for an unchanged file and reads original bytes. `testChanged()` appends data after the original status and expects open to either allow changed content or throw `InvalidPathHandleException` according to `HandleOpt.Data`. `testMoved()` renames after status capture and checks `HandleOpt.Location`. `testChangedAndMoved()` combines rename and append. Additional tests open handles through `openFile().build().thenApply(readStream)`, delete the target before async open and accept `FileNotFoundException` or `InvalidPathHandleException`, and verify successful lazy open for existing handles.

State and persistence behavior: each test creates a method-named file with deterministic bytes. Some tests append, rename, or delete the target after acquiring status or handle, then validate whether the handle remains valid. Serialization is simulated by converting handle bytes into `RawPathHandle`.

Dependencies and integration points: the file uses contract flags `SUPPORTS_FILE_REFERENCE` and `SUPPORTS_CONTENT_CHECK` as skip gates. It relies on append and rename utilities and on the target filesystem implementing handle option semantics precisely.

Risks: a one-second sleep works around second-precision timestamps in raw local filesystems, but timing-based content checks remain sensitive. Support for content and reference validation is optional, so coverage depends on concrete contract settings.

Test signals: pass indicates path handles can reopen stable files, serialized handles round-trip, content and location change policies are enforced, async open by handle behaves like path open, and deleted targets fail lazily with a recognized exception.
