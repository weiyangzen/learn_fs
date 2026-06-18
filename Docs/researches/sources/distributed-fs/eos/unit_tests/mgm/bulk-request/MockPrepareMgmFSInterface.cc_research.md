# sources/distributed-fs/eos/unit_tests/mgm/bulk-request/MockPrepareMgmFSInterface.cc

## sources/distributed-fs/eos/unit_tests/mgm/bulk-request/MockPrepareMgmFSInterface.cc

Purpose: provides concrete static lambda implementations used by prepare-manager tests to simulate MGM filesystem outcomes without a real namespace or tape backend.

Important APIs and types: implements static `std::function` members declared in `MockPrepareMgmFSInterface.hh`. The lambdas target `IMgmFileSystemInterface` methods: `_exists`, `_attr_ls`, `_stat`, and `_access`. It uses `SFS_OK`, `SFS_ERROR`, `XrdSfsFileExistIsFile`, `XrdSfsFileExistNo`, `XRDSFS_HASBKUP`, and `XRDSFS_OFFLINE`.

Control flow: existence lambdas set output references and return success or error. Attribute-list lambdas populate xattr maps with stage, abort, evict, retrieve-error, archive-error, request-id, and request-time keys. Stat lambdas encode disk/tape state via `st_rdev` bits or set an error in `XrdOucErrInfo`. Access lambdas return allow or deny.

State and persistence: static function objects are process-wide test helpers. They mutate only caller-owned output arguments; no persistent state is stored beyond constants.

Dependencies and integration: depends on EOS common constants for xattr names and XRootD stat flags. The behavior feeds both `PrepareManagerTest.cc` and `BulkRequestPrepareManagerTest.cc`.

Risks and test signals: these lambdas are part of the test oracle. If production logic changes xattr names, stat flag interpretation, or permission checks, tests may fail because the mock no longer mirrors production. Static mutable test helpers can also hide inter-test coupling if reassigned elsewhere.
