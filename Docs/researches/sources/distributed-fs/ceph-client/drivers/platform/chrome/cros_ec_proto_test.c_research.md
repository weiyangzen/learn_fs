# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_proto_test.c

## Purpose
`cros_ec_proto_test.c` is the KUnit suite for the Chrome EC protocol helper layer. It creates a synthetic `struct cros_ec_device`, queues mock transfer responses through `cros_ec_proto_test_util`, and asserts protocol helper behavior without real EC hardware.

## Important APIs, Types, and Functions
- `struct cros_ec_proto_test_priv` owns the fake `cros_ec_device`, static `din`/`dout` buffers, and reusable command storage.
- `cros_ec_proto_test_init()` initializes a KUnit-owned device, mock transfer callbacks, buffers, mutex, and default protocol state.
- The suite covers `cros_ec_prepare_tx()`, `cros_ec_check_result()`, `cros_ec_query_all()`, `cros_ec_cmd_xfer()`, `cros_ec_cmd_xfer_status()`, `cros_ec_get_next_event()`, `cros_ec_get_host_event()`, `cros_ec_check_features()`, `cros_ec_get_sensor_count()`, and `cros_ec_cmd()`.
- `KUNIT_CASE()` entries enumerate more than 50 focused behavioral cases.

## Control Flow
Each test queues one or more mock transfer objects, calls a public protocol helper, then drains completed mocks to verify the exact EC command, version, input/output sizes, request payload, return value, and mutated EC state. Protocol-discovery tests call a pretest helper that nulls `din`/`dout` because the production code frees and reallocates those pointers using devm APIs. In-progress command tests rely on default mock return values or explicit `EC_CMD_GET_COMMS_STATUS` responses to exercise retry loops.

## State and Persistence
All state is KUnit-scoped. The fake device has statically backed buffers except where `cros_ec_query_all()` reallocates devm buffers. Mocks are reset in `cros_ec_proto_test_init()` for each test, so queued transfers, call counters, readmem data, and default return values do not persist across cases. Static `struct cros_ec_dev` instances in feature and sensor tests are deliberately overwritten before use.

## Dependencies and Integration Points
The test depends on KUnit, Chrome EC command/protocol headers, `cros_ec.h`, and `cros_ec_proto_test_util.h`. It validates public helpers exported by `cros_ec_proto.c` and the internal contract expected by transport callbacks: transfer callbacks observe populated command headers and overwrite `msg->data` and `msg->result`.

## Risks and Edge Cases
The tests heavily encode exact command order for protocol discovery and feature probing, so changes to discovery sequence require updating expectations. They validate many failures, including zero-length EC responses, invalid legacy hello data, missing transport callbacks, outsize limits for normal and passthrough commands, unsupported MKBP/host-sleep/wake-mask commands, and `EC_RES_IN_PROGRESS` retries. The test file does not exercise physical SPI/RPMsg checksum parsing directly; it isolates protocol-level logic.

## Test Signals
This file is itself the primary test signal for `cros_ec_proto.c`. Passing the `cros_ec_proto_test` suite indicates command framing, negotiation, error mapping, event handling, feature caching, and sensor count compatibility behavior match expected contracts.
