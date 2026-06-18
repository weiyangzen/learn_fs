# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_proto_test_util.h

## Purpose
`cros_ec_proto_test_util.h` declares the KUnit mock transfer objects and helper functions used by Chrome EC protocol tests.

## Important APIs, Types, and Functions
- `struct ec_xfer_mock` records a queued/completed transfer: list node, owning KUnit test, captured input data, configured return/result/output data, output length, and a trailing `struct cros_ec_command` snapshot.
- Extern globals expose default mock return/result, command and packet transfer counters, readmem offset/data/return values.
- Function declarations cover transfer mocks, mock queue management, readmem mock, and reset.

## Control Flow
The header is included by test code and the mock implementation. Tests allocate/queue mocks through the declared helpers, install the transfer functions into `struct cros_ec_device`, and inspect completed `ec_xfer_mock` records returned by `cros_kunit_ec_xfer_mock_next()`.

## State and Persistence
The header itself stores no state but exposes mutable globals defined in the `.c` file. The trailing `struct cros_ec_command msg` is documented as last because it ends in a flexible-array member, which affects layout expectations.

## Dependencies and Integration Points
It depends on `linux/platform_data/cros_ec_proto.h` for `struct cros_ec_device` and `struct cros_ec_command`; it also relies on KUnit and list types being available through including translation units.

## Risks and Edge Cases
Because the header exposes globals directly, tests can accidentally leave stale defaults unless reset is called. The flexible-array-member comment on `msg` is important: adding fields after it would be a layout bug.

## Test Signals
This header enables protocol KUnit coverage by publishing the mock API used throughout `cros_ec_proto_test.c`.
