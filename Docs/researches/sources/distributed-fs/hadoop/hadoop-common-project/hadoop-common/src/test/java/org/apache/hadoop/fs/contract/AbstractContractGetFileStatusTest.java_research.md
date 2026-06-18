# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractGetFileStatusTest.java

Purpose: `AbstractContractGetFileStatusTest` is the central listing/status contract suite. It validates `getFileStatus`, `listStatus`, `listStatusIterator`, `listLocatedStatus`, `listFiles`, filtering, iterator behavior, and metadata consistency.

Important APIs and types: it uses `FileStatus`, `LocatedFileStatus`, `RemoteIterator`, `FilterFileSystem`, `PathFilter`, `TreeScanResults`, and many `ContractTestUtils` helpers. Constants define a small generated tree: depth 2, width 3, four files per directory, 512 byte files.

Control flow: `setup()` skips if `SUPPORTS_GETFILESTATUS` is absent. Basic tests cover missing status, root status, empty directory listings, and missing path errors for every listing API. `testComplexDirActions()` creates a test tree once, then checks non-recursive `listStatus`, `listStatusIterator`, `listLocatedStatus`, non-recursive `listFiles`, and recursive `listFiles`. It compares listings with generated tree data and tree walks. Iterator tests consume iterators both with ordinary `hasNext()/next()` and through `next()` calls alone. File-as-input tests confirm listing a file returns a single file entry. Filtering tests validate `PathFilter` behavior on directories, files, and empty directories.

State and persistence behavior: helper methods delete and recreate the contract test root, generate random subfolder names for empty directory tests, and create a deterministic nested tree for complex listings. No durable state beyond test artifacts is intended.

Dependencies and integration points: the file depends heavily on `ContractTestUtils.TreeScanResults` for comparing file and directory sets. `ExtendedFilterFS` exposes protected `listLocatedStatus(Path, PathFilter)` so the filter path is tested through the standard `FilterFileSystem` layer.

Risks: object stores with eventual listing consistency may fail unless their contract layer stabilizes results. Iterator implementations that require `hasNext()` before `next()` are explicitly caught. Owner comparisons in `verifyFileStats()` may expose inconsistent listing metadata even when paths and lengths are correct.

Test signals: pass indicates status calls throw expected missing-path exceptions, root is a directory, listing APIs agree on directory and file contents, iterator contracts are robust, recursive file listing matches tree walk, filters are honored, and located statuses match direct file statuses for core fields.
