<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/uuid_kunit.c -->
# sources/distributed-fs/ceph-client/lib/tests/uuid_kunit.c

## Purpose
KUnit tests for UUID/GUID parsing in `lib/uuid.c`, validating byte ordering for GUID and UUID forms and rejection of malformed strings.

## APIs, Types, and Functions
Defines `struct test_uuid_data` with a canonical UUID string, expected little-endian `guid_t`, and expected big-endian `uuid_t`. Tests call `guid_parse()`, `uuid_parse()`, `guid_equal()`, and `uuid_equal()`.

## Control Flow, State, and Persistence
Valid tests iterate `test_uuid_test_data`, parse each string into a local object, and compare against `GUID_INIT()` or `UUID_INIT()` constants. Invalid tests iterate strings missing hyphens, containing invalid hex, or containing insufficient data, expecting `-EINVAL`. There is no mutable state.

## Dependencies and Integration
Depends on KUnit and `linux/uuid.h`. It registers as the `uuid` suite and directly covers the parser used by kernel subsystems accepting textual UUIDs.

## Risks and Test Signals
Risks include limited invalid formats, no uppercase-string coverage, and no direct test for `uuid_is_valid()` or random generation. Test signals are explicit GUID-vs-UUID endian expectations and common parse-failure cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/tests/uuid_kunit.c -->
