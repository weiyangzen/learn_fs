<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/acl_converter_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/acl_converter_unittest.cc

## Purpose

This file contains intended ACL converter fixtures and tests, but the actual test bodies are commented out.

## Important APIs, Types, and Functions

Fixtures `kMinimalXattr` and `kExtendedXattr` encode POSIX ACL xattr byte sequences. Commented tests describe minimal, extended, and failed ACL conversion checks.

## Control Flow

No active test control flow is compiled besides includes and fixture definitions. The commented flow would extract POSIX/xattr data, convert to ACL, serialize back, and mutate fixture bytes to verify failures.

## State and Persistence Behavior

No runtime state is created by active tests.

## Dependencies and Integration Points

It includes `acl_converter.h` and GoogleTest, but currently contributes no assertions.

## Risks and Edge Cases

Because all meaningful tests are disabled, regressions in endian handling, id validation, tag ordering, and malformed xattr rejection can pass the test suite unnoticed.

## Test Signals

The current signal is only compile coverage. Re-enabling and updating these tests would provide direct converter validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/acl_converter_unittest.cc -->
