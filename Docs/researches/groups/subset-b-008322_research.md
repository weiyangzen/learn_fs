# subset-b-008322 research

Grouped research report for subset `subset-b-008322`. Each section is bounded by source-path markers for deterministic reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppDirTest_Timestamps.h -->
# sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppDirTest_Timestamps.h

Purpose: typed GoogleTest timestamp coverage for `fspp::Dir` operations and directory-entry side effects across concrete filesystem fixtures. It validates that creating files, directories, and symlinks mutates the parent directory mtime/ctime but not atime, and that new children receive current atime/mtime/ctime values.

Important APIs/types/functions: `FsppDirTest_Timestamps`, `FsppDirTest_Timestamps_Entries`, `createAndOpenFile`, `createDir`, `createSymlink`, `children`, `remove`, `rename`, `REGISTER_TYPED_TEST_SUITE_P`, and `REGISTER_NODE_TEST_SUITE`.

Control flow: each test builds an operation closure, resets the fixture through `TimestampTestUtils::testBuilder`, runs the closure under all atime policies, and compares pre/post `stat_info` timestamps. Child-entry tests inherit `FsppNodeTest` to run file, directory, and symlink variants.

State and persistence behavior: tests create transient directory trees through the abstract `Device`; timestamps are persisted in node metadata and reloaded with `Load`. Root-directory timestamp cases are deliberately commented out due known root timestamp handling gaps.

Dependencies and integration points: relies on `TimestampTestUtils`, `FileSystemTest`, `FsppNodeTest`, `cpputils::time`, and fspp directory APIs. It integrates with concrete fspp backends via typed-test instantiation.

Risks and test signals: strong coverage of POSIX-like timestamp semantics for directory mutations and listing, including noatime/strictatime/relatime/nodiratime behavior. Known risk is disabled root-directory coverage, which leaves `/` timestamp behavior unguarded.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppDirTest_Timestamps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppFileTest.h -->
# sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppFileTest.h

Purpose: reusable typed tests for the `fspp::File` interface, covering open modes, truncation, ownership/mode mutation, explicit `utimens`, and removal for root and nested files.

Important APIs/types/functions: `FsppFileTest<ConcreteFileSystemTestFixture>`, `Test_Open_RDONLY`, `Test_Open_WRONLY`, `Test_Open_RDWR`, `Test_Truncate_*`, `Test_Chown_*`, `Test_Chmod`, `Test_Utimens`, `Remove`, and `REGISTER_TYPED_TEST_SUITE_P`.

Control flow: fixture members from `FileTest` provide root and nested file handles plus node handles. Tests call file or node methods, then assert through helper methods that node stat and open-file stat agree and readable size matches expected bytes.

State and persistence behavior: truncation grows and shrinks file content state; ownership, mode, and timestamps are persisted through `Node::stat`; removal verifies both generic `Load` and typed `LoadFile` return `boost::none`.

Dependencies and integration points: depends on `FileTest`, `fspp::File`, `fspp::Node`, `fspp::OpenFile`, typed GoogleTest registration, and fspp strongly typed wrappers such as `num_bytes_t`, `uid_t`, `gid_t`, and `mode_t`.

Risks and test signals: good basic contract coverage, but `Test_Open_RDWR` calls `RDONLY()` instead of `RDWR()`, likely weakening intended read-write mode coverage. TODOs note that some node-interface cases should move to node tests and that timestamp effects are covered elsewhere.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppFileTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppFileTest_Timestamps.h -->
# sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppFileTest_Timestamps.h

Purpose: timestamp-specific tests for `fspp::File` operations before an `OpenFile` is used. It verifies open operations do not affect timestamps and file-level truncation updates mtime and ctime.

Important APIs/types/functions: `FsppFileTest_Timestamps`, `CreateFileWithSize`, `open(fspp::openflags_t)`, `truncate`, and timestamp expectation helpers from `TimestampTestUtils`.

Control flow: helper creates a file and optionally truncates it to a known size. Each typed test returns a move-capturing operation closure and evaluates expected timestamp deltas under all atime configurations.

State and persistence behavior: the file size is set through `File::truncate` and verified via `Load(path)->stat`. Tests compare metadata around operations rather than content bytes.

Dependencies and integration points: relies on `TimestampTestUtils`, `FileSystemTest::CreateFile`, `Load`, `stat`, and fspp open-flag constructors. Registered as a typed suite for concrete filesystem implementations.

Risks and test signals: establishes that open is metadata-neutral for no mode, read-only, write-only, and read-write flags. Truncation expectations update mtime/ctime even when truncating zero to zero, which may intentionally encode CryFS semantics but differs from some filesystem optimizations.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppFileTest_Timestamps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppNodeTest_Rename.h -->
# sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppNodeTest_Rename.h

Purpose: node-generic rename behavior tests run against file, directory, and symlink nodes. It covers success paths, overwrite behavior, error propagation, and validity of a node object after repeated renames.

Important APIs/types/functions: `FsppNodeTest_Rename`, `Node::rename`, `Device::Load`, `Dir::children`, `FuseErrnoException`, and `REGISTER_NODE_TEST_SUITE`.

Control flow: `REGISTER_NODE_TEST_SUITE` expands the same `Test_*` methods into file-node, dir-node, and symlink-node typed fixtures. Tests create source and target trees, execute rename, then assert loadability or expected errno values.

State and persistence behavior: rename moves directory entries and may replace existing nodes. Error tests assert that original nodes remain loadable, while overwrite count tests ensure replaced entries do not duplicate directory children.

Dependencies and integration points: depends on `FsppNodeTest`, `FileSystemTest`, `boost::none`, and FUSE errno translation via `fspp::fuse::FuseErrnoException`.

Risks and test signals: covers `ENOENT`, `ENOTDIR`, `EBUSY`, `EISDIR`, cross-directory moves, self-renames, and replace semantics. TODOs identify missing invariant checks for stat fields and contents across rename success and failure paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppNodeTest_Rename.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppNodeTest_Stat.h -->
# sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppNodeTest_Stat.h

Purpose: typed stat tests for generic nodes plus node-kind-specific stat assertions for files, directories, and symlinks.

Important APIs/types/functions: `FsppNodeTest_Stat`, `FsppNodeTest_Stat_FileOnly`, `FsppNodeTest_Stat_DirOnly`, `FsppNodeTest_Stat_SymlinkOnly`, `Node::stat`, and `mode_t` flag checks.

Control flow: generic node tests run via `REGISTER_NODE_TEST_SUITE`; file-only, dir-only, and symlink-only suites directly create typed nodes and inspect `Node::stat_info`.

State and persistence behavior: tests create nodes and immediately load/stat them. They verify nlink, size, and mode-kind bits, without mutating persistent content beyond fixture setup.

Dependencies and integration points: uses `FsppNodeTest`, `FileSystemTest`, `FsppNodeTestHelper::IN_STAT`, and concrete fixtures supplied through typed-test instantiation.

Risks and test signals: provides basic stat contract signals but intentionally shallow coverage. TODO notes more stat cases are needed, such as permissions, ownership, timestamps, and potentially link counts for directories.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppNodeTest_Stat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppNodeTest_Timestamps.h -->
# sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppNodeTest_Timestamps.h

Purpose: node-generic timestamp contract tests for files, directories, and symlinks. It covers creation, stat/access neutrality, chmod/chown/utimens ctime behavior, rename timestamp behavior, and rename error paths.

Important APIs/types/functions: `FsppNodeTest_Timestamps`, `Test_Create`, `Test_Stat`, `Test_Chmod`, `Test_Chown`, `Test_Access`, `Test_Rename_*`, `Test_Utimens`, `FuseErrnoException`, and `REGISTER_NODE_TEST_SUITE`.

Control flow: tests build closures that mutate or inspect a node, then pass either one path or old/new paths into `EXPECT_OPERATION_UPDATES_TIMESTAMPS_AS`. Rename success compares old-path stat before with new-path stat after, while error paths compare the same path.

State and persistence behavior: exercises metadata stored in `Node::stat_info`; rename updates the node ctime but not atime/mtime; failed renames should leave timestamps unchanged. `utimens` explicitly changes atime/mtime and expects ctime to move to operation time.

Dependencies and integration points: mixes `FsppNodeTest` and `TimestampTestUtils`, requiring virtual inheritance through `FileSystemTest`. Uses fspp context atime policies and POSIX-like errno values.

Risks and test signals: broad cross-node timestamp coverage. Root-dir rename timestamp test is disabled because root timestamp storage is known incomplete; overwrite cases verify source node ctime but do not fully validate target deletion metadata side effects.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppNodeTest_Timestamps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppOpenFileTest.h -->
# sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppOpenFileTest.h

Purpose: minimal typed tests for the `fspp::OpenFile` interface, focused on stat behavior for newly created files.

Important APIs/types/functions: `FsppOpenFileTest`, `IN_STAT`, `EXPECT_SIZE`, `EXPECT_NUMBYTES_READABLE`, `OpenFile::stat`, `OpenFile::read`, and `File::open`.

Control flow: creates a file, reopens it read-only, then asserts size and file mode through open-file stat. Readability helper attempts to read one byte past expected size and verifies exactly expected bytes are readable.

State and persistence behavior: no long-lived mutation beyond file creation; validates that open-file view reflects persisted file metadata and that empty files read as zero bytes.

Dependencies and integration points: inherits `FileSystemTest`; uses `cpputils::Data`, fspp byte-count wrappers, and typed GoogleTest registration for concrete backends.

Risks and test signals: only covers empty file stat and file-kind mode. TODOs list substantial missing coverage for open-file truncate/read/write/flush/fsync/fdatasync and create-and-open stat behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppOpenFileTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppOpenFileTest_Timestamps.h -->
# sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppOpenFileTest_Timestamps.h

Purpose: timestamp behavior tests for `fspp::OpenFile` operations, including stat, truncate, read, write, flush, fsync, and fdatasync.

Important APIs/types/functions: `FsppOpenFileTest_Timestamps`, `CreateAndOpenFile`, `CreateAndOpenFileWithSize`, `OpenFile`, `OpenFile::read`, `write`, `truncate`, `flush`, `fsync`, `fdatasync`, and `EXPECT_OPERATION_UPDATES_TIMESTAMPS_AS`.

Control flow: helper methods create files and open them `RDWR`; tests capture an `OpenFile*` plus a move-owned closure and evaluate expected timestamp changes under each atime mode. Read tests vary atime relative to mtime and whether reads are in bounds or partially beyond requested range.

State and persistence behavior: open-file truncation changes size and mtime/ctime; reads may update atime depending on context; writes update mtime/ctime; flush/fsync/fdatasync are expected timestamp-neutral after the preceding write.

Dependencies and integration points: relies on `TimestampTestUtils`, `FileSystemTest` atime-state setters, `std::array`, fspp open flags, and concrete filesystem fixture reset behavior.

Risks and test signals: strong matrix for relatime/noatime/nodiratime semantics on file reads. The "outofbounds" read cases still read from offset 2 in a 10-byte file for 5 bytes, so naming suggests intended boundary coverage may be incomplete.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppOpenFileTest_Timestamps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppSymlinkTest.h -->
# sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppSymlinkTest.h

Purpose: basic typed tests for symlink creation, target reading, and removal in root and nested directories.

Important APIs/types/functions: `FsppSymlinkTest`, `CreateSymlink`, `LoadSymlink`, `Symlink::target`, `Node::remove`, and typed GoogleTest registration.

Control flow: creates symlinks with absolute and relative target strings, reloads them through typed symlink access, and compares `target()` results. Remove tests verify both generic and symlink-specific load paths disappear.

State and persistence behavior: symlink target text is persisted as node data; removal updates directory entries and makes the node unavailable through `Device`.

Dependencies and integration points: uses `FileSystemTest`, `boost::none`, fspp `Symlink`, and concrete typed fixtures.

Risks and test signals: validates basic symlink functionality but does not cover invalid targets, overwrite semantics, directory timestamp side effects, or permission-related behavior. Timestamp coverage is delegated to the paired timestamp test file.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppSymlinkTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppSymlinkTest_Timestamps.h -->
# sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppSymlinkTest_Timestamps.h

Purpose: timestamp tests for reading a symlink target under different atime policies.

Important APIs/types/functions: `FsppSymlinkTest_Timestamps`, `Symlink::target`, `setAtimeNewerThanMtimeButBeforeYesterday`, `setAtimeOlderThanMtime`, `setAtimeNewerThanMtime`, and timestamp expectation helpers.

Control flow: each test creates a symlink, forces a specific atime/mtime relationship, captures a closure that calls `target()`, then runs expectations across noatime, strictatime, relatime, nodiratime+relatime, and nodiratime+strictatime contexts.

State and persistence behavior: metadata is mutated by `utimens` in setup and then compared around target reads. Since symlinks are not directories, nodiratime modes behave like their corresponding file/symlink atime modes.

Dependencies and integration points: inherits from `TimestampTestUtils`; integrates with `FileSystemTest::CreateSymlink` and fspp context updates.

Risks and test signals: covers relatime edge cases for symlink target reads. It does not test symlink creation timestamps directly or failure modes for missing/corrupt symlink target metadata.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/FsppSymlinkTest_Timestamps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/testutils/FileSystemTest.h -->
# sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/testutils/FileSystemTest.h

Purpose: base fixture utilities for typed fspp filesystem tests. It abstracts creation of concrete `fspp::Device` instances and provides common load/create helpers and timestamp-state setup.

Important APIs/types/functions: `FileSystemTestFixture::createDevice`, `FileSystemTest`, `resetFilesystem`, `MODE_PUBLIC`, `Load`, `LoadDir`, `LoadFile`, `LoadSymlink`, `CreateDir`, `CreateFile`, `CreateSymlink`, `EXPECT_IS_*`, and atime relation setters.

Control flow: constructor resets the filesystem with `relatime` context. `resetFilesystem` recreates the concrete fixture and device, then installs the requested `fspp::Context`. Load helpers assert `boost::optional` is present before moving out `unique_ref`.

State and persistence behavior: tests operate on a fresh device per reset. Creation helpers mutate parent directories; atime setup methods read current stat, alter times, and persist them through `utimens`.

Dependencies and integration points: depends on GoogleTest, Boost, `cpputils::unique_ref`, fspp `Device/Node/Dir/File/Symlink/OpenFile`, and context timestamp policies.

Risks and test signals: central helper consistency is critical because many tests assume its atime setup creates exact relative relationships by changing nanoseconds only; edge cases around nanosecond underflow/overflow could affect timestamp tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/testutils/FileSystemTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/testutils/FileTest.h -->
# sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/testutils/FileTest.h

Purpose: file-specific fixture setup and assertion helpers shared by `FsppFileTest`.

Important APIs/types/functions: `FileTest`, constructor-created `file_root`, `file_nested`, node mirrors, `IN_STAT`, `EXPECT_SIZE`, `EXPECT_NUMBYTES_READABLE`, `EXPECT_ATIME_EQ`, and `EXPECT_MTIME_EQ`.

Control flow: constructor creates `/myfile`, `/mydir/mynestedfile`, and `/mydir2`. Assertions compare stat from both generic node and open-file views, then validate read length by reading one byte past expected size.

State and persistence behavior: fixture pre-populates root and nested file entries. Size assertions rely on persisted file data and metadata being visible through separate file and node handles.

Dependencies and integration points: inherits `FileSystemTest`; uses `cpputils::Data`, `unique_ref`, fspp file APIs, and typed byte-count wrappers.

Risks and test signals: strengthens file tests by checking both stat surfaces and actual readable byte count. Constructor state is broad and may mask tests that accidentally depend on preexisting `/mydir2`.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/testutils/FileTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/testutils/FsppNodeTest.h -->
# sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/testutils/FsppNodeTest.h

Purpose: macro and fixture infrastructure for writing one node test suite that runs against files, directories, and symlinks.

Important APIs/types/functions: `FsppNodeTestHelper`, `FsppNodeTest`, `CreateNode`, `_REGISTER_*_TEST_SUITE`, `REGISTER_NODE_TEST_SUITE`, and `INSTANTIATE_NODE_TEST_SUITE`.

Control flow: macros generate three derived fixture classes per test suite. Each derived class implements `CreateNode` by creating the appropriate node kind and loading it as a generic `fspp::Node`; Boost.Preprocessor expands each `Test_Name` method into a typed GoogleTest case.

State and persistence behavior: generated tests create concrete nodes through `FileSystemTest` helpers and then exercise generic node behavior against persisted backend state.

Dependencies and integration points: uses Boost.Preprocessor, GoogleTest typed tests, fspp node APIs, and virtual inheritance to combine helpers cleanly.

Risks and test signals: avoids duplicated file/dir/symlink tests, but macro expansion can obscure compile errors and makes registration order important. Create-node paths always create fresh nodes and do not cover preexisting-node collisions.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/testutils/FsppNodeTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/testutils/TimestampTestUtils.h -->
# sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/testutils/TimestampTestUtils.h

Purpose: shared timestamp assertion framework for fspp tests, including reusable expectations and a builder that repeats checks under all supported atime policies.

Important APIs/types/functions: `TimestampTestUtils`, `TimestampUpdateExpectation`, `EXPECT_OPERATION_UPDATES_TIMESTAMPS_AS` overloads, `EXPECT_*_TIMESTAMP_BETWEEN`, `stat`, `xSecondsAgo`, `ensureNodeTimestampsAreOld`, `TestBuilder`, and static expectation lambdas.

Control flow: captures old stat, waits until the clock progresses, records operation bounds, executes the operation, captures new stat, and applies each expectation. Builder methods reset the filesystem with noatime, strictatime, relatime, nodiratime+relatime, or nodiratime+strictatime.

State and persistence behavior: resets discard prior fixture state between atime modes. Timestamp comparison depends on filesystem metadata persistence and nanosecond-resolution clock progress.

Dependencies and integration points: depends on `cpputils::time`, `cpputils::stat`, `FileSystemTest`, fspp `Context`, `Node`, and `OpenFile`.

Risks and test signals: centralizes precise ctime/mtime/atime expectations. Busy-wait clock progression is intentionally fast but can spin under coarse clocks; operation-bound comparisons can be flaky if filesystem timestamp precision is lower than `timespec`.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fstest/testutils/TimestampTestUtils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fuse/CMakeLists.txt -->
# sources/security-integrity/cryfs/old-cpp/src/fspp/fuse/CMakeLists.txt

Purpose: CMake build definition for the static `fspp-fuse` adapter library.

Important APIs/types/functions: CMake target `fspp-fuse`, sources `FilesystemImpl.cpp`, `Profiler.cpp`, `Fuse.cpp`, compile definition `_FILE_OFFSET_BITS=64`, Boost helper macros, Dokan configuration, and `PkgConfig::Fuse`.

Control flow: always builds a static library and links `cpp-utils` plus `fspp-interface`. On Windows it locates Dokan by architecture and installs required DLLs; on Linux/macOS it requires pkg-config and FUSE.

State and persistence behavior: no runtime state, but `_FILE_OFFSET_BITS=64` affects ABI and large-file stat behavior for all consumers of the target.

Dependencies and integration points: integrates with platform FUSE/Dokan libraries, CMake helper functions, Boost, and the fspp interface target.

Risks and test signals: architecture branch hard-fails unsupported Windows targets. FUSE dependency is mandatory outside Windows. macOS sets `CMAKE_FIND_FRAMEWORK LAST` after FUSE setup, which may affect dependency resolution globally in this directory scope.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fuse/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fuse/stat_compatibility.h -->
# sources/security-integrity/cryfs/old-cpp/src/fspp/fuse/stat_compatibility.h

Purpose: small platform compatibility header that gives fspp FUSE code a single `fspp::fuse::STAT` type across POSIX FUSE and Windows Dokan.

Important APIs/types/functions: namespace `fspp::fuse`, typedef `STAT`, `_MSC_VER` branch, `FUSE_STAT`, and POSIX `struct stat`.

Control flow: preprocessor selects Dokan/FUSE's `FUSE_STAT` under MSVC and `::stat` elsewhere.

State and persistence behavior: no state; this is an ABI/typing shim used by code that fills stat structures.

Dependencies and integration points: includes `<fuse.h>` on MSVC and `<sys/stat.h>` otherwise. It is consumed by FUSE adapter code that wants one stat spelling.

Risks and test signals: correctness depends on Dokan's `FUSE_STAT` being layout-compatible with expected stat fields. Non-MSVC Windows compilers would take the POSIX branch, which may be wrong for Dokan builds.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/fspp/fuse/stat_compatibility.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/parallelaccessstore/CMakeLists.txt -->
# sources/security-integrity/cryfs/old-cpp/src/parallelaccessstore/CMakeLists.txt

Purpose: CMake build definition for the `parallelaccessstore` static library.

Important APIs/types/functions: target `parallelaccessstore`, sources `ParallelAccessBaseStore.cpp` and `ParallelAccessStore.cpp`, `target_link_libraries(cpp-utils)`, Boost helper, style warnings, and C++14 activation.

Control flow: declares a static library from two translation units, though most implementation lives in headers due templates.

State and persistence behavior: no runtime state; build target exposes parallel access abstractions to block/blob store layers.

Dependencies and integration points: links `cpp-utils` and Boost support, and participates in the old C++ CryFS build graph.

Risks and test signals: source `.cpp` files only include headers, so build coverage mostly verifies template headers compile in at least one target but does not instantiate all combinations.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/parallelaccessstore/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/parallelaccessstore/ParallelAccessBaseStore.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/parallelaccessstore/ParallelAccessBaseStore.cpp

Purpose: translation unit for `ParallelAccessBaseStore.h`.

Important APIs/types/functions: includes `ParallelAccessBaseStore.h`; no additional functions or state are defined.

Control flow: none beyond compilation of the header in a source target.

State and persistence behavior: no runtime state.

Dependencies and integration points: exists so CMake can list a concrete source file for the static library and so the header participates in normal compilation.

Risks and test signals: empty implementation means all behavior resides in interface implementations elsewhere; no direct test signal is produced by this file alone beyond build success.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/parallelaccessstore/ParallelAccessBaseStore.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/parallelaccessstore/ParallelAccessBaseStore.h -->
# sources/security-integrity/cryfs/old-cpp/src/parallelaccessstore/ParallelAccessBaseStore.h

Purpose: abstract base-store interface used by `ParallelAccessStore` to load and remove keyed resources from the underlying persistent store.

Important APIs/types/functions: template `ParallelAccessBaseStore<Resource, Key>`, virtual destructor, `loadFromBaseStore`, `removeFromBaseStore(unique_ref<Resource>)`, and `removeFromBaseStore(const blockstore::BlockId&)`.

Control flow: pure virtual interface only; implementers supply load/remove semantics.

State and persistence behavior: abstracts persistent resource access. Loading returns optional ownership of a resource; removal can be by loaded resource or by key.

Dependencies and integration points: uses `cpputils::unique_ref`, `boost::optional`, and `blockstore::BlockId`. The template key type is generic, but one remove overload is fixed to `BlockId`, coupling the interface to blockstore IDs.

Risks and test signals: mixed generic `Key` and concrete `BlockId` in removal is an API smell and may constrain reuse. Implementations must honor ownership and deletion guarantees expected by `ParallelAccessStore`.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/parallelaccessstore/ParallelAccessBaseStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/parallelaccessstore/ParallelAccessStore.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/parallelaccessstore/ParallelAccessStore.cpp

Purpose: translation unit for the template implementation in `ParallelAccessStore.h`.

Important APIs/types/functions: includes `ParallelAccessStore.h`; no non-template implementation is defined here.

Control flow: none at runtime.

State and persistence behavior: no direct state; all stateful behavior is header-defined in the template.

Dependencies and integration points: included in the `parallelaccessstore` library target to compile the header in normal builds.

Risks and test signals: since template code is header-only, this file does not instantiate common template combinations or catch all template errors. Behavior must be validated by downstream instantiations and tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/parallelaccessstore/ParallelAccessStore.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/parallelaccessstore/ParallelAccessStore.h -->
# sources/security-integrity/cryfs/old-cpp/src/parallelaccessstore/ParallelAccessStore.h

Purpose: keyed resource manager that prevents concurrent duplicate loads, tracks open references, and defers base-store removal until all references to a resource are released.

Important APIs/types/functions: `ParallelAccessStore<Resource, ResourceRef, Key>`, nested `ResourceRefBase`, `OpenResource`, `isOpened`, `add`, `load`, `loadOrAdd`, `remove`, `_resourceToRemoveFuture`, and `release`.

Control flow: `load` locks globally, returns an existing open resource ref or loads from base store and adds it. `ResourceRefBase` destructor calls `release`, decrementing ref count. `remove` registers a promise, destroys or waits for refs to drain, then removes from base store.

State and persistence behavior: `_openResources` owns live resources by key and ref count; `_resourcesToRemove` holds promises for resources pending deletion. Underlying persistence is delegated to `ParallelAccessBaseStore`.

Dependencies and integration points: uses `std::mutex`, `unordered_map`, `boost::promise/future`, `cpputils::unique_ref`, `ASSERT`, and resource refs that must inherit `ResourceRefBase`.

Risks and test signals: file has explicit TODOs about locking, global serialization, race conditions, and missing tests. `remove(const Key&)` reads `_openResources` without taking `_mutex` before `_resourceToRemoveFuture`, which is a concurrency risk.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/parallelaccessstore/ParallelAccessStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/stats/CMakeLists.txt -->
# sources/security-integrity/cryfs/old-cpp/src/stats/CMakeLists.txt

Purpose: builds the `cryfs-stats` executable.

Important APIs/types/functions: target `stats`, sources `main.cpp` and `traversal.cpp`, link libraries `cryfs`, `cpp-utils`, `gitversion`, and output name `cryfs-stats`.

Control flow: declares an executable, links dependencies, enables style warnings and C++14, and renames the generated binary.

State and persistence behavior: no runtime state in the build file; it wires the stats tool into the build.

Dependencies and integration points: depends on the main CryFS library plus utility and version targets.

Risks and test signals: no tests are registered here; correctness is inferred from executable build and any manual/integration use of `cryfs-stats`.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/stats/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/stats/main.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/stats/main.cpp

Purpose: command-line `cryfs-stats` tool that opens an encrypted CryFS basedir read-only, prints configuration, finds all on-disk blocks, subtracts blocks reachable from filesystem blobs, and reports unaccounted block depths.

Important APIs/types/functions: `makeBlobStore`, `makeBlockStore`, `AccumulateBlockIds`, `ProgressBar`, `getKnownBlobIds`, `getKnownBlockIds`, `getAllBlockIds`, `printConfig`, and `main`.

Control flow: validates one argument, prompts for password, loads config read-only, checks format compatibility, enumerates all block IDs, recursively traverses reachable blobs and their blocks, erases accounted IDs from a set, then prints orphan/unaccounted leaf versus inner node counts.

State and persistence behavior: uses local state directory integrity data and opens Rust bridge stores in read-only locking/integrity/encrypted mode. It does not mutate the filesystem, but it may read integrity metadata and emits warnings on integrity violations.

Dependencies and integration points: integrates `CryConfigLoader`, password-based key provider with SCrypt, Rust block/blob-store bridge factories, `LocalStateDir`, `IOStreamConsole`, and traversal helpers.

Risks and test signals: assertions assume reachable references always exist on disk. Password prompting and full block traversal make this a manual diagnostic tool; no direct automated tests in this subset cover it.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/stats/main.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/stats/traversal.cpp -->
# sources/security-integrity/cryfs/old-cpp/src/stats/traversal.cpp

Purpose: traversal helper implementations for `cryfs-stats`.

Important APIs/types/functions: `forEachBlock`, `forEachReachableBlob`, `forEachReachableBlockInBlob`, `BlockStore::forEachBlock`, `RustFsBlobStore::load`, `RustDirBlob::AppendChildrenTo`, and `DataBlob::allBlocks`.

Control flow: `forEachBlock` forwards every block ID to callbacks. `forEachReachableBlob` recursively visits root and directory children by block ID. `forEachReachableBlockInBlob` loads a blob and invokes callbacks for every block listed by `allBlocks`.

State and persistence behavior: read-only traversal of block/blob stores; recursion depends on persisted directory entries and blob child references.

Dependencies and integration points: uses Rust fsblobstore types, fspp directory entries, `cpputils::dynamic_pointer_move`, `boost::none`, and `ASSERT`.

Risks and test signals: recursive traversal can stack-overflow on very deep trees and has no cycle guard; it assumes directory child lists and lookups remain internally consistent. No automated tests here validate corrupted stores.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/stats/traversal.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/stats/traversal.h -->
# sources/security-integrity/cryfs/old-cpp/src/stats/traversal.h

Purpose: public declarations for stats traversal helpers over block stores and Rust filesystem blob stores.

Important APIs/types/functions: `cryfs_stats::forEachBlock`, `forEachReachableBlob`, `forEachReachableBlockInBlob`, callback vectors of `std::function<void(const BlockId&)>`.

Control flow: declaration-only header; callers pass a store pointer, root ID where applicable, and callback list.

State and persistence behavior: functions are intended for read-only enumeration of existing blocks and reachable blob/block graphs.

Dependencies and integration points: includes blockstore interfaces and `RustFsBlobStore`; consumed by `main.cpp`.

Risks and test signals: API passes raw pointers and does not encode nullability or ownership. Header typo names `blobtore` in one parameter, harmless for ABI but a readability issue.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/src/stats/traversal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/CMakeLists.txt -->
# sources/security-integrity/cryfs/old-cpp/test/CMakeLists.txt

Purpose: top-level CMake test tree entry point.

Important APIs/types/functions: `BUILD_TESTING`, `include_directories(../src)`, and `add_subdirectory` calls for test support and component test suites.

Control flow: only active when `BUILD_TESTING` is true. Adds gtest main, gitversion, cpp-utils, fspp except on MSVC, parallelaccessstore, blockstore, blobstore, cryfs, and cryfs-cli tests.

State and persistence behavior: no runtime state; configures which tests are built.

Dependencies and integration points: integrates all old C++ test subdirectories with source includes.

Risks and test signals: fspp tests are disabled on MSVC due a TODO, leaving Windows-specific fspp/Dokan behavior less covered.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blobstore/CMakeLists.txt -->
# sources/security-integrity/cryfs/old-cpp/test/blobstore/CMakeLists.txt

Purpose: CMake definition for the `blobstore-test` executable.

Important APIs/types/functions: target `blobstore-test`, source list for onblocks utility, blob store, blob size/read/write, big blob, and data tree tests; link to `my-gtest-main`, `googletest`, and `blobstore`; `add_test`.

Control flow: compiles all listed unit tests into one executable and registers it with CTest.

State and persistence behavior: no runtime state in the build file; tests use in-memory/fake stores.

Dependencies and integration points: connects blobstore implementation tests to the project test harness and C++14/style warning helpers.

Risks and test signals: source list is explicit, so new tests are not picked up automatically. It currently includes Rust bridge blobstore fixtures even though directory names still say `onblocks`.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blobstore/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/BigBlobsTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/BigBlobsTest.cpp

Purpose: regression tests ensuring blob operations work above the 4 GiB boundary and do not use 32-bit size arithmetic.

Important APIs/types/functions: `BigBlobsTest`, constants `SMALL_BLOB_SIZE`, `LARGE_BLOB_SIZE`, `Blob::resize`, `write`, `read`, `flush`, `blockId`, `BlobStore::load`, and `remove`.

Control flow: creates an in-memory Rust blob store, resizes across the 4 GiB threshold, writes sparse ranges near/after that threshold, reloads blobs, and compares generated fixture data.

State and persistence behavior: blob size and sparse data are persisted through the blob store and validated after reload in the resize test.

Dependencies and integration points: uses Rust bridge `RustBlobStore`, compressing in-memory store factory, `DataFixture`, and `cpputils::destruct`.

Risks and test signals: excellent signal for 64-bit offsets, but tests can be expensive in memory/time if backing implementation materializes sparse data. TODO notes `Blob::readAll` above 4 GiB remains untested.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/BigBlobsTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/BlobReadWriteTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/BlobReadWriteTest.cpp

Purpose: read/write behavior tests for blobs, including empty reads, zero-byte writes, partial overwrites, full-range reads, and persistence after reloading.

Important APIs/types/functions: `BlobReadWriteTest`, `BlobReadWriteDataTest`, `DataRange`, `readBlob`, `EXPECT_DATA_READS_AS`, `EXPECT_DATA_IS_ZEROES_OUTSIDE_OF`, `Blob::tryRead`, `read`, `readAll`, `write`, `resize`, and `blockId`.

Control flow: fixture creates random data and a blob. Basic tests cover empty and zero-size behavior. Parameterized tests run many offset/count/blob-size combinations across single-leaf and large multi-leaf blobs.

State and persistence behavior: writes modify blob content and may grow size; reload tests destruct and reload by `BlockId` to verify persisted data and zero-filled untouched ranges.

Dependencies and integration points: inherits `BlobStoreTest`, uses `DataNodeLayout` to choose leaf boundaries, and relies on `DataFixture` for deterministic content.

Risks and test signals: broad coverage of boundary ranges and partial updates. It expects `read` beyond blob size to throw while `tryRead` returns zero; implementation changes must preserve that API split.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/BlobReadWriteTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/BlobSizeTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/BlobSizeTest.cpp

Purpose: blob size and resize semantics tests.

Important APIs/types/functions: `BlobSizeTest`, `BlobSizeDataTest`, `Blob::size`, `resize`, `write`, `read`, `blockId`, and `loadBlob`.

Control flow: tests grow, shrink, resize-to-self, reload after size changes, and write at/after/over end. Data tests verify zero-fill and data retention when growing, shrinking, and regrowing.

State and persistence behavior: validates that size metadata persists across destruction/reload and that truncated regions are not resurrected after regrowth.

Dependencies and integration points: inherits `BlobStoreTest`, uses `DataFixture` for random data and `cpputils::Data` zero buffers.

Risks and test signals: strong coverage for resize invariants and sparse growth zeroing. Large sizes are 5-10 MiB here, so 64-bit overflow coverage is delegated to `BigBlobsTest`.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/BlobSizeTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/BlobStoreTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/BlobStoreTest.cpp

Purpose: basic blob-store lifecycle tests for unique IDs and deletion.

Important APIs/types/functions: `BlobStoreTest`, `BlobStore::create`, `load`, `remove`, `Blob::blockId`, and `reset`.

Control flow: creates blobs, compares IDs, removes blobs directly, by key, and after reload, then verifies load returns empty.

State and persistence behavior: deletion must remove persisted blob state such that subsequent loads by `BlockId` fail.

Dependencies and integration points: uses `BlobStoreTest` fixture, Boost optional helpers, and blockstore `BlockId`.

Risks and test signals: covers simple lifecycle behavior only; concurrent open references, double deletion, and remove error cases are not covered here.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/BlobStoreTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/datatreestore/DataTreeTest_Performance.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/datatreestore/DataTreeTest_Performance.cpp

Purpose: performance-contract tests for `DataTree` traversal, deletion, and resizing, measured by mock block-store load/create/remove/write/resize counters.

Important APIs/types/functions: `DataTreeTest_Performance`, `TraverseByWriting`, `TraverseByReading`, `DataTreeStore::remove`, `DataTree::writeBytes`, `readBytes`, `resizeNumBytes`, and `MockBlockStore` counters.

Control flow: builds specific two-level/three-level/four-level tree shapes, resets block-store counters, performs an operation, and asserts exact counts of loaded, created, removed, written, and resized blocks.

State and persistence behavior: tree structure persists as data nodes in a mock block store. Tests ensure operations mutate only necessary tree nodes and avoid loading leaves when overwriting full ranges.

Dependencies and integration points: inherits `DataTreeTest`, relies on `DataNodeLayout` limits, `MockBlockStore`, and data tree store implementation.

Risks and test signals: very high signal for algorithmic regressions and accidental I/O amplification. Exact counter expectations are brittle when legitimate internal traversal strategies change.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/datatreestore/DataTreeTest_Performance.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/datatreestore/LeafTraverserTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/datatreestore/LeafTraverserTest.cpp

Purpose: unit tests for `LeafTraverser`, verifying which leaves are visited or created across tree depths and ranges.

Important APIs/types/functions: `LeafTraverserTest`, `TraversorMock`, `LeafTraverser::traverseAndUpdateRoot`, `LeafHandle`, `EXPECT_TRAVERSE_LEAF`, `EXPECT_CREATE_LEAF`, `CreateThreeLevel`, and `CreateFourLevel`.

Control flow: constructs known tree shapes, sets gmock expectations for leaf callbacks, flushes/loads the tree, invokes `traverseAndUpdateRoot`, and checks whether root ownership changes in read-only versus mutating traversals.

State and persistence behavior: traverser may update root and create new leaves when growing ranges. Read-only traversal must leave the root pointer unchanged; mutating traversal may replace root.

Dependencies and integration points: inherits `DataTreeTest`, uses gmock matchers, `DataNodeStore`, `DataInnerNode`, `DataLeafNode`, and `DataTreeStore`.

Risks and test signals: extensive coverage of first/middle/last ranges in two-, three-, and four-level trees. Tests encode exact leaf index mapping and right-border semantics, which are core to safe data tree updates.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/datatreestore/LeafTraverserTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/datatreestore/testutils/DataTreeTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/datatreestore/testutils/DataTreeTest.cpp

Purpose: implementation of reusable data-tree test fixture helpers for constructing, loading, and validating synthetic tree shapes.

Important APIs/types/functions: `DataTreeTest::DataTreeTest`, `CreateLeaf`, `CreateInner`, `CreateLeafOnlyTree`, `FillNode`, `FillNodeTwoLevel`, `CreateFullTwoLevel`, `CreateFullThreeLevel`, `LoadInnerNode`, `LoadLeafNode`, size-specific tree builders, `EXPECT_IS_*`, and `CHECK_DEPTH`.

Control flow: fixture wires a `MockBlockStore` into a `DataNodeStore` and `DataTreeStore`. Helpers create leaf/inner nodes, fill children to layout limits, load and cast nodes, and recursively validate depth.

State and persistence behavior: all constructed nodes are persisted in the mock block store and addressed by `BlockId`; helper methods may resize last leaves to model partial trees.

Dependencies and integration points: uses `DataNodeStore`, `DataTreeStore`, `MockBlockStore`, `dynamic_pointer_move`, and `cpputils::unique_ref`.

Risks and test signals: centralizes tree topology setup for many tests. Some helpers pass temporary-created node pointers into `CreateInner`; correctness depends on node creation persisting before temporary ownership is destroyed.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/datatreestore/testutils/DataTreeTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/datatreestore/testutils/DataTreeTest.h -->
# sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/datatreestore/testutils/DataTreeTest.h

Purpose: declaration of reusable data-tree test fixture and helper API.

Important APIs/types/functions: `DataTreeTest`, `BLOCKSIZE_BYTES`, tree construction helpers, node loading helpers, fixture fields `_blockStore`, `blockStore`, `_nodeStore`, `nodeStore`, `treeStore`, validation helpers, and `CHECK_DEPTH`.

Control flow: header exposes helpers used by data tree performance and traverser tests; implementation is in `DataTreeTest.cpp`.

State and persistence behavior: fixture owns a mock block store and data node store, while `treeStore` owns the node store after construction. Raw observer pointers allow tests to inspect counters and layout.

Dependencies and integration points: includes GoogleTest, `FakeBlockStore`, `MockBlockStore`, data node/tree store headers, and block IDs.

Risks and test signals: raw observer pointers depend on ownership staying valid inside `treeStore`. Copy/assign is disabled to avoid duplicating ownership-heavy fixture state.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/datatreestore/testutils/DataTreeTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/datatreestore/testutils/LeafDataFixture.h -->
# sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/datatreestore/testutils/LeafDataFixture.h

Purpose: helper for filling a data leaf with deterministic fixture bytes and later verifying those bytes.

Important APIs/types/functions: `LeafDataFixture`, constructor `(size, iv)`, `FillInto`, `EXPECT_DATA_CORRECT`, and private `loadData`.

Control flow: constructor generates data through `DataFixture`. `FillInto` resizes and writes a leaf. Verification reads the leaf into a buffer and compares full or prefix bytes.

State and persistence behavior: mutates `DataLeafNode` size and content. Data is stored in `_data` for expected comparison.

Dependencies and integration points: uses GoogleTest assertions, `cpputils::DataFixture`, `DataLeafNode::resize`, `write`, and `read`.

Risks and test signals: useful for content preservation checks. Optional prefix verification only asserts at least the requested bytes exist and does not verify bytes beyond the prefix.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/datatreestore/testutils/LeafDataFixture.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/datatreestore/testutils/TwoLevelDataFixture.h -->
# sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/datatreestore/testutils/TwoLevelDataFixture.h

Purpose: recursive fixture helper for filling and verifying leaf data across a data-node tree, despite the historical "TwoLevel" name.

Important APIs/types/functions: `TwoLevelDataFixture`, `SizePolicy::{Random, Full, Unchanged}`, `FillInto`, `EXPECT_DATA_CORRECT`, `ForEachLeaf`, and `size`.

Control flow: recursively walks `DataNode` trees with dynamic casts. For each leaf in the selected range, it creates a `LeafDataFixture` using deterministic seed/leaf index and fills or checks content.

State and persistence behavior: loads child nodes from `DataNodeStore`, mutates leaf sizes/content during fill, and verifies persisted leaf bytes during checks.

Dependencies and integration points: uses `DataNodeStore`, `DataInnerNode`, `DataLeafNode`, `LeafDataFixture`, `cpputils::ASSERT`, and dynamic casts.

Risks and test signals: recursion supports more than two levels, but no cycle protection exists. `SizePolicy::Random` uses modular arithmetic to avoid negative sizes; incorrect layout limits would affect fixture generation.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/datatreestore/testutils/TwoLevelDataFixture.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/testutils/BlobStoreTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/testutils/BlobStoreTest.cpp

Purpose: implementation of the blob-store test fixture constructor.

Important APIs/types/functions: `BlobStoreTest::BLOCKSIZE_BYTES`, `BlobStoreTest::BlobStoreTest`, `RustBlobStore`, and `new_locking_inmemory_blobstore`.

Control flow: initializes `blobStore` with a Rust bridge in-memory blob store using the fixture block size.

State and persistence behavior: each test fixture gets an isolated in-memory blob store; persistence is limited to the lifetime of that fixture instance.

Dependencies and integration points: includes `RustBlobStore` and cpputils GCC compatibility header. A commented line shows a previous/onblocks fake-store implementation path.

Risks and test signals: tests under `onblocks` names now exercise Rust bridge blob store behavior, so directory naming may mislead. In-memory backing avoids disk flakiness but may not expose on-disk persistence issues.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/testutils/BlobStoreTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/testutils/BlobStoreTest.h -->
# sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/testutils/BlobStoreTest.h

Purpose: shared GoogleTest fixture for blob-store tests.

Important APIs/types/functions: `BlobStoreTest`, `BLOCKSIZE_BYTES`, `blobStore`, `loadBlob`, and `reset`.

Control flow: constructor is defined in the `.cpp`; helper `loadBlob` asserts `BlobStore::load` succeeds and moves out the loaded blob. `reset` consumes a blob ref to trigger destruction.

State and persistence behavior: owns a `unique_ref<BlobStore>` for each test. `reset` intentionally drops blob ownership so later loads validate store persistence.

Dependencies and integration points: includes GoogleTest and `blobstore/interface/BlobStore.h`; used by blob size/read/write/lifecycle tests.

Risks and test signals: `reset` relies on move-destruction side effects and can look like a no-op to readers. Helper asserts load success, so tests cannot inspect failure details through it.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/testutils/BlobStoreTest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/utils/CeilDivisionTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/utils/CeilDivisionTest.cpp

Purpose: unit tests for `ceilDivision` math helper.

Important APIs/types/functions: `CeilDivisionTest`, `ceilDivision`, and 64-bit integer constants.

Control flow: checks divisions by 4, 1, 2, equal operands, and a 64-bit value larger than `uint32_t::max`.

State and persistence behavior: pure function tests with no state.

Dependencies and integration points: includes `blobstore/implementations/onblocks/utils/Math.h`, GoogleTest, and `<limits>`. The helper is used by blob/data tree sizing logic.

Risks and test signals: good boundary coverage for exact and non-exact division. Does not cover division by zero, which should either be disallowed by contract or asserted elsewhere.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/utils/CeilDivisionTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/utils/CeilLogTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/utils/CeilLogTest.cpp

Purpose: unit tests for `ceilLog` math helper.

Important APIs/types/functions: `CeilLogTest`, `ceilLog`, and 64-bit value checks.

Control flow: verifies base-3 logs around powers and non-powers, plus base-1024 log for a 1 TiB value.

State and persistence behavior: pure function tests with no state.

Dependencies and integration points: includes `Math.h`, GoogleTest, and `<limits>`. Used by tree-depth or layout calculations.

Risks and test signals: confirms representative small and 64-bit cases. TODO indicates broader cases are still needed; invalid bases and zero values are not covered.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/utils/CeilLogTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/utils/IntPowTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/utils/IntPowTest.cpp

Purpose: unit tests for integer exponentiation helper `intPow`.

Important APIs/types/functions: `IntPowTest`, `intPow`, and 64-bit power case.

Control flow: covers zero exponent, zero base, exponent one, powers of two and ten, arbitrary bases, and a 64-bit base cubed.

State and persistence behavior: pure function tests with no state.

Dependencies and integration points: includes blobstore math helper and GoogleTest. Math results feed blob/data-tree layout sizing.

Risks and test signals: broad normal-case coverage. It does not test overflow behavior, so callers must avoid values that exceed the return type.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/utils/IntPowTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/utils/MaxZeroSubtractionTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/utils/MaxZeroSubtractionTest.cpp

Purpose: unit tests for saturating subtraction helper `maxZeroSubtraction`.

Important APIs/types/functions: `MaxZeroSubtractionTest`, `maxZeroSubtraction`, `numeric_limits<uint32_t>::max`, and 64-bit cases.

Control flow: verifies equal operands return zero, positive differences are preserved, negative differences saturate at zero, subtraction from zero stays zero, and 64-bit values work.

State and persistence behavior: pure function tests with no state.

Dependencies and integration points: includes blobstore `Math.h`, GoogleTest, and `<limits>`.

Risks and test signals: strong edge coverage around unsigned underflow prevention. Overflow in the input expressions themselves is not explored.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blobstore/implementations/onblocks/utils/MaxZeroSubtractionTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/CMakeLists.txt -->
# sources/security-integrity/cryfs/old-cpp/test/blockstore/CMakeLists.txt

Purpose: CMake definition for the `blockstore-test` executable.

Important APIs/types/functions: target `blockstore-test`, sources `BlockStoreUtilsTest.cpp` and `ParallelAccessBlockStoreTest_Specific.cpp`, link libraries `my-gtest-main`, `googletest`, and `blockstore`, plus `add_test`.

Control flow: builds and registers the blockstore test executable when parent testing is enabled.

State and persistence behavior: no runtime state; test behavior is in listed source files and subdirectories.

Dependencies and integration points: connects blockstore tests to the project CTest harness and build warning/C++14 helpers.

Risks and test signals: the cache test files in this subset are not listed directly here, implying they may be included by another nested CMake file or omitted from this old test target.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/CacheTest_MoveConstructor.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/CacheTest_MoveConstructor.cpp

Purpose: tests that `Cache` uses move construction when possible and only copies when an lvalue is pushed.

Important APIs/types/functions: `CacheTest_MoveConstructor`, `Cache<MinimalKeyType, CopyableMovableValueType, 100>`, `push`, `pop`, and `CopyableMovableValueType::numCopyConstructorCalled`.

Control flow: resets copy counter, pushes either a temporary or lvalue, pops it, touches the value to prevent optimization, and asserts copy count.

State and persistence behavior: cache holds in-memory key/value entries; test state is the static copy counter.

Dependencies and integration points: uses `Cache`, minimal test key/value types, `cpputils::unique_ref`, and GoogleTest.

Risks and test signals: verifies efficient ownership transfer. It does not inspect move-constructor count, only absence/presence of copies.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/CacheTest_MoveConstructor.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/CacheTest_PushAndPop.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/CacheTest_PushAndPop.cpp

Purpose: functional tests for cache insertion, lookup/removal, capacity eviction, ordering, and age timeout behavior.

Important APIs/types/functions: `CacheTest_PushAndPop`, fixture helpers `push` and `pop`, `MAX_ENTRIES`, `Cache::MAX_LIFETIME_SEC`, and `Cache::PURGE_LIFETIME_SEC`.

Control flow: tests empty, non-empty, and full cache misses; ordered and non-ordered push/pop sequences; eviction when exceeding capacity; and timeout eviction using sleeps around two inserted entries.

State and persistence behavior: all cache entries are in-memory. Pop removes entries; pushing beyond capacity evicts oldest entries; background/age cleanup affects timeout test.

Dependencies and integration points: uses `testutils/CacheTest.h`, `Cache`, minimal key/value types, Boost optional helpers, and Boost thread sleep.

Risks and test signals: good coverage of FIFO-like eviction and keyed pop. Timeout test depends on wall-clock timing and can be slow or flaky under heavy load.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/CacheTest_PushAndPop.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/CacheTest_RaceCondition.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/CacheTest_RaceCondition.cpp

Purpose: regression tests for a cache race where `pop()` could return before an evicted entry's destructor finished writing back data.

Important APIs/types/functions: `ObjectWithLongDestructor`, `CacheTest_RaceCondition`, `ConditionBarrier`, `causeCacheOverflowInOtherThread`, `EXPECT_POP_BLOCKS_UNTIL_DESTRUCTOR_FINISHED`, and `EXPECT_POP_DOESNT_BLOCK_UNTIL_DESTRUCTOR_FINISHED`.

Control flow: pushes an object whose destructor signals start and sleeps. Tests trigger age-based or capacity-based eviction, wait until destruction starts, then call `pop` for either the same key or another key and assert blocking behavior.

State and persistence behavior: cache entries are in-memory, but the destructor models delayed persistence/writeback. Atomic `destructorFinished` records completion.

Dependencies and integration points: uses `Cache`, `std::async`, `std::atomic`, `ConditionBarrier`, and move-only `unique_ptr` values.

Risks and test signals: strong concurrency regression signal for requested-key eviction synchronization. Tests rely on sleeps and async scheduling, so timing failures are possible on constrained systems.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/CacheTest_RaceCondition.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/PeriodicTaskTest.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/PeriodicTaskTest.cpp

Purpose: tests lifecycle and callback behavior for `PeriodicTask`.

Important APIs/types/functions: `AtomicCounter`, `PeriodicTaskTest`, `PeriodicTask`, `waitForZero`, and callback lambdas.

Control flow: constructs a task and destroys it immediately, waits for at least ten rapid callbacks using a condition variable, and verifies no callback runs after task destruction.

State and persistence behavior: in-memory background task state only; atomic/counter objects track callback execution.

Dependencies and integration points: uses `PeriodicTask`, mutex/condition variable, atomics, GoogleTest, and Boost thread sleep.

Risks and test signals: covers destructor deadlock and post-destruction callback safety. Timing-based tests with 1 ms periods can be sensitive to scheduler delays.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/PeriodicTaskTest.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/QueueMapTest_MemoryLeak.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/QueueMapTest_MemoryLeak.cpp

Purpose: verifies `QueueMap` correctly constructs and destroys key/value objects despite custom memory management.

Important APIs/types/functions: `QueueMapTest_MemoryLeak`, `EXPECT_NUM_INSTANCES`, `MinimalKeyType::instances`, `MinimalValueType::instances`, `push`, `pop`, and keyed `pop`.

Control flow: executes push/pop sequences and compares live instance counters after each scenario.

State and persistence behavior: queue-map in-memory entries own key/value instances; counters reflect live object state.

Dependencies and integration points: inherits `QueueMapTest` fixture and uses minimal test key/value types.

Risks and test signals: strong leak/double-destruction signal for common pop paths. It does not cover replacement of an existing key unless helper behavior includes it elsewhere.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/QueueMapTest_MemoryLeak.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/QueueMapTest_MoveConstructor.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/QueueMapTest_MoveConstructor.cpp

Purpose: tests that `QueueMap` uses move construction for rvalue values and copy construction for lvalue values.

Important APIs/types/functions: `QueueMapTest_MoveConstructor`, `QueueMap<MinimalKeyType, CopyableMovableValueType>`, `push`, `pop`, keyed `pop`, and copy counter.

Control flow: pushes temporary and lvalue values, pops by FIFO or key, and checks the copy-constructor counter.

State and persistence behavior: in-memory queue/map entries only; static counter records constructor behavior.

Dependencies and integration points: uses `QueueMap`, `MinimalKeyType`, `CopyableMovableValueType`, `cpputils::unique_ref`, and GoogleTest.

Risks and test signals: validates efficient value storage across both pop APIs. It does not test move-only values directly.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/QueueMapTest_MoveConstructor.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/QueueMapTest_Peek.cpp -->
# sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/QueueMapTest_Peek.cpp

Purpose: tests non-destructive `QueueMap::peek` behavior.

Important APIs/types/functions: `QueueMapPeekTest`, fixture helpers `push`, `peek`, `pop`, and keyed `pop`.

Control flow: checks empty peek, repeated peek after one or two pushes, interaction between peek and FIFO pop, and peek after removing the first key directly.

State and persistence behavior: queue-map maintains insertion order; `peek` must not remove entries, while keyed pop updates both map and queue ordering.

Dependencies and integration points: inherits `QueueMapTest`, uses Boost optional I/O helper for assertions, and minimal key/value fixture types.

Risks and test signals: verifies peek idempotence and consistency after keyed removal. It does not cover peeking after capacity-like bulk operations because QueueMap itself does not enforce capacity here.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/old-cpp/test/blockstore/implementations/caching/cache/QueueMapTest_Peek.cpp -->
