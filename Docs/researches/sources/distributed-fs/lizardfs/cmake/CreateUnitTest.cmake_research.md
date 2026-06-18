# sources/distributed-fs/lizardfs/cmake/CreateUnitTest.cmake

## Purpose
This module defines helper functions for registering unit-test libraries and their link dependencies when tests are enabled.

## Important APIs, Types, and Functions
`create_unittest(TEST_NAME ...)` returns unless `BUILD_TESTS` is true and sources were provided. It removes the test name from `ARGV`, creates a library named `${TEST_NAME}_unittest`, includes GTest headers, and appends the test name to cached `UNITTEST_TEST_NAMES`. `link_unittest(TEST_NAME ...)` stores link libraries in cached `${TEST_NAME}_UNITTEST_LINKLIST`.

## Control Flow and State
Both helpers use CMake internal cache variables as a cross-directory registry. They avoid doing any work when tests are disabled.

## Dependencies and Integration Points
They rely on `GTEST_INCLUDE_DIRS` from dependency discovery and on later unit-test aggregation logic in the source tree that consumes `UNITTEST_TEST_NAMES` and per-test link lists.

## Risks and Edge Cases
Because state is cached with `FORCE`, stale test registration can persist across configure changes unless cache is cleared carefully. The functions silently return with too few args, which can hide misconfigured tests.

## Test Signals
When `ENABLE_TESTS` is on, generated unit-test libraries and cache variables should appear. Link failures or absent tests indicate missing `create_unittest` or `link_unittest` calls.
