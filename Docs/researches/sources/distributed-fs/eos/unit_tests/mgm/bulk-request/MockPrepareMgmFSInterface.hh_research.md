# sources/distributed-fs/eos/unit_tests/mgm/bulk-request/MockPrepareMgmFSInterface.hh

## sources/distributed-fs/eos/unit_tests/mgm/bulk-request/MockPrepareMgmFSInterface.hh

Purpose: declares a GoogleMock implementation of `IMgmFileSystemInterface` for prepare-manager tests, plus reusable static lambdas and constants describing common filesystem states.

Important APIs and types: `MockPrepareMgmFSInterface` mocks `addStats`, `isTapeEnabled`, `getReqIdMaxCount`, `Emsg`, overloaded `_exists`, `_attr_ls`, `_access`, `FSctl`, `_stat`, `_stat_set_flags`, `get_logId`, `get_host`, and `writeEosReportRecord`. It also exposes lambdas for file existence, directory workflow xattrs, query xattrs, stat states, and permission outcomes.

Control flow: the header is declarative; tests configure `ON_CALL` and `EXPECT_CALL` with either simple returns or `Invoke(...)` using the static lambdas. The mocked surface is broad enough to exercise stage, cancel, evict, and query prepare logic.

State and persistence: no instance state beyond gmock bookkeeping. Static constants include error strings, retrieve request id/time, and a regex for EOS report records.

Dependencies and integration: includes MGM namespace support, XRootD error and security entities, virtual identity, namespace xattr maps, and the bulk request filesystem interface. It is the central adapter between unit tests and prepare-manager dependencies.

Risks and test signals: overloaded mock methods must match production signatures exactly. Broad mocking makes interaction tests precise but can be brittle if implementation order or call grouping changes without changing external behavior.
