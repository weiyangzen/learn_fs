# sources/distributed-fs/ceph/src/rgw/driver/dbstore/tests/CMakeLists.txt

## Purpose
Defines unit-test targets for the dbstore backend.

## APIs, Flow, And State
Builds `unittest_dbstore_tests` from `dbstore_tests.cc` and `unittest_dbstore_mgr_tests` from `dbstore_mgr_tests.cc`. Links the first target with accumulated `CMAKE_LINK_LIBRARIES` plus gtest, and the manager target with `dbstore` and `gtest_main`. Both are registered with `add_ceph_unittest()` and get VLA warnings as errors when supported.

## Dependencies And Integration
Depends on gtest, Ceph test macros, and the `dbstore` target. It integrates the manager tests read in this work item and broader dbstore tests outside this exact item.

## Risks And Test Signals
The file does not explicitly link SQLite here; that is expected through the `dbstore` target. Coverage is only as broad as the two source files. The primary signal is successful target build and execution under Ceph’s unit-test runner.
