# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_proto_test_util.c

## Purpose
`cros_ec_proto_test_util.c` implements reusable KUnit mocks for Chrome EC command transfers and EC memory reads. It lets protocol tests queue deterministic fake EC responses, capture submitted commands, and count which transport path was selected.

## Important APIs, Types, and Functions
- `cros_kunit_ec_xfer_mock()` is the base mock transfer callback. It pops a queued `ec_xfer_mock`, copies the submitted command and output payload for later inspection, injects `result` and response data into the caller command, and returns the configured transfer return value.
- `cros_kunit_ec_cmd_xfer_mock()` and `cros_kunit_ec_pkt_xfer_mock()` wrap the base mock and increment v2/v3 path counters.
- `cros_kunit_ec_xfer_mock_add()` creates a successful response mock whose return length equals response size.
- `cros_kunit_ec_xfer_mock_addx()` creates a mock with explicit return code, EC result, and response payload size.
- `cros_kunit_ec_xfer_mock_next()` returns the next completed mock for assertions.
- `cros_kunit_readmem_mock()` simulates `cmd_readmem`.
- `cros_kunit_mock_reset()` resets globals and list heads.

## Control Flow
Tests enqueue input mocks on `cros_kunit_ec_xfer_mock_in`. When production code calls a transfer callback, the mock removes the first queued item, snapshots `struct cros_ec_command`, optionally copies outbound command data into KUnit memory, fills the command result and inbound data from the mock output payload, then moves the mock to the output list. Tests call `cros_kunit_ec_xfer_mock_next()` to verify the transaction after the helper returns.

## State and Persistence
State is held in file-scope globals: default EC result/return code, transport call counters, two mock lists, readmem offset/data/return value. `cros_kunit_mock_reset()` must be called before each test to avoid cross-test contamination. Mock objects and payloads are allocated from the test context, so KUnit owns cleanup.

## Dependencies and Integration Points
The utility depends on KUnit allocation/assertion infrastructure, Linux list helpers, Chrome EC command/protocol headers, and the local `struct ec_xfer_mock` declaration from the companion header. It integrates with `struct cros_ec_device` by being assigned to `cmd_xfer`, `pkt_xfer`, or `cmd_readmem`.

## Risks and Edge Cases
`cros_kunit_ec_xfer_mock_addx()` allocates zero bytes for zero-size responses through `kunit_kzalloc(test, size, ...)`; callers currently assert non-NULL, so changes in KUnit zero-size allocation semantics could affect tests. The readmem mock assumes `cros_kunit_readmem_mock_data` is valid and large enough for `bytes`. Default transfer behavior is used when the input queue is empty, which is useful for retry tests but can hide missing explicit mocks if call counters are not asserted.

## Test Signals
The utility supports all protocol KUnit tests. Its most important signal is accurate capture of command metadata and payloads, plus separate call counters proving protocol v2 uses `cmd_xfer` and protocol v3 uses `pkt_xfer`.
