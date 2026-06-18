# sources/distributed-fs/eos/unit_tests/mgm/bulk-request/PrepareManagerTest.cc

## sources/distributed-fs/eos/unit_tests/mgm/bulk-request/PrepareManagerTest.cc

Purpose: tests the non-bulk `PrepareManager` workflows for option stringification, argument wrapping, stage, cancel, evict, and query behavior.

Important APIs and types: `PrepareManager`, `PrepareUtils`, `PrepareArgumentsWrapper`, `QueryPrepareResult`, `MockPrepareMgmFSInterface`, `ClientWrapper`, `ErrorWrapper`, and XRootD return codes `SFS_OK`, `SFS_DATA`, and `SFS_ERROR`.

Control flow: stage tests validate successful workflow execution, duplicated path handling, no-path behavior, all-missing files, and one missing file. Cancel and evict tests mirror existence and workflow-xattr flows but expect different aggregate outcomes. Query tests construct a `QueryPrepareResult` and assert per-file fields including path order, online status, tape status, existence, request-id presence, request time, and error text.

State and persistence: no external persistence. The manager owns the injected mock interface. Query responses preserve input ordering, including duplicates, which is a key state contract for callers.

Dependencies and integration: tests calls into `IMgmFileSystemInterface` for existence, xattr listing, stat, access, `FSctl`, MGM logging identity, host identity, and EOS report records. It also covers xattr-derived retrieve/archive error propagation.

Risks and test signals: call counts encode implementation details. More importantly, tests document that plain `PrepareManager` is stricter than the bulk manager in some missing-file cancel/evict cases. Query behavior around permissions and tape/disk flags is high-risk because callers depend on exact status fields and user-facing error text.
