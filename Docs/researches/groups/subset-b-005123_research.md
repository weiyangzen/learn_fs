# Research: subset-b-005123

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_proto.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_proto.c

## Purpose
`cros_ec_proto.c` is the shared ChromeOS Embedded Controller protocol helper layer. It sits above physical transports such as SPI and RPMsg and below feature drivers such as sensorhub, sysfs, and Type-C. It prepares protocol v2/v3 wire packets, chooses the transport callback, serializes EC commands through `ec_dev->lock`, negotiates protocol capabilities, maps EC status codes to Linux errors, handles long-running `EC_RES_IN_PROGRESS` commands, and exposes helper APIs for events, features, sensor counts, memmap access, command-version queries, and command wrappers.

## Important APIs, Types, and Functions
- `cros_ec_prepare_tx()` selects legacy v2 framing or v3 `ec_host_request` framing.
- `cros_ec_check_result()` only treats `EC_RES_IN_PROGRESS` specially, preserving older ABI behavior where most EC result values are not converted at this stage.
- `cros_ec_query_all()` negotiates protocol v3 with `EC_CMD_GET_PROTOCOL_INFO`, falls back to v2 `EC_CMD_HELLO`, sizes `din`/`dout`, probes MKBP, host sleep v1, and host event wake masks.
- `cros_ec_cmd_xfer()` is the serialized raw command API. It lazily calls `cros_ec_query_all()` if the protocol is unknown, clamps receive size, enforces request and passthrough limits, sends the command, and leaves EC result interpretation to callers.
- `cros_ec_cmd_xfer_status()` wraps `cros_ec_cmd_xfer()` and converts EC result codes via `cros_ec_map_error()`.
- `cros_ec_get_next_event()` reads MKBP events, handles legacy keyboard-state fallback, adjusts supported MKBP version after `EC_RES_INVALID_VERSION`, and computes wake-event hints.
- `cros_ec_check_features()`, `cros_ec_get_sensor_count()`, `cros_ec_cmd()`, `cros_ec_cmd_readmem()`, `cros_ec_get_cmd_versions()`, and `cros_ec_device_registered()` are exported convenience APIs used by other Chrome EC drivers.

## Control Flow
Outgoing command flow starts in `cros_ec_cmd_xfer()` or `cros_ec_cmd_xfer_status()`, enters the device mutex, confirms protocol limits, then calls `cros_ec_send_command()`. `cros_ec_send_command()` delegates to `cros_ec_xfer_command()`, which picks `pkt_xfer` for protocol versions greater than 2 and `cmd_xfer` for v2. Request/response tracing is emitted around the transport callback. If the EC returns `EC_RES_IN_PROGRESS`, the helper polls `EC_CMD_GET_COMMS_STATUS` up to 50 times with 10 ms sleeps until processing clears or an error/timeout occurs.

Protocol discovery first assumes v3, then asks the primary EC for packet sizes and protocol bitmasks. It optionally probes a PD passthrough device, then allocates buffers sized to max packet size plus overhead. If v3 discovery fails, v2 discovery sends `EC_CMD_HELLO` and validates the fixed response value before constraining sizes to `EC_PROTO2_MAX_PARAM_SIZE`. Event flow uses negotiated MKBP version to choose v0, v1/v2, or capped v3 response layout, caches `ec_dev->event_data`, masks `EC_MKBP_HAS_MORE_EVENTS`, and derives wake-event decisions from sensor FIFO, RTC, and wake-mask state.

## State and Persistence
The file mutates runtime-only `struct cros_ec_device` state: protocol version, max request/response sizes, passthrough size, buffer pointers/sizes, MKBP support level, host sleep capability, host event wake mask, event payload/size, and registered flag. Feature probing caches the `struct ec_response_get_features` bitmap in `struct cros_ec_dev` by using all-ones as an uninitialized sentinel. Sensor count probing has a legacy LPC/memmap fallback. There is no durable storage; persistence is in device lifetime memory and devm allocations.

## Dependencies and Integration Points
It depends on Chrome EC command definitions in `cros_ec_commands.h`, core device definitions in `cros_ec_proto.h`, transport callbacks supplied by bus drivers, and tracepoints in `cros_ec_trace.h`. It integrates with notifier/event consumers via `event_data`, with sensorhub via `cros_ec_get_sensor_count()` and sensor FIFO event retrieval, with sysfs and Type-C through `cros_ec_cmd()`, and with all bus drivers through `cros_ec_prepare_tx()` and `cros_ec_check_result()`.

## Risks and Edge Cases
Protocol negotiation must handle early EC unavailability; failure leaves `proto_version` unknown so the first real command can retry discovery. Buffer sizing is critical because v3 request/response sizes subtract host headers while transport buffers include overhead. `EC_RES_IN_PROGRESS` polling can take roughly half a second and returns `-EAGAIN` if the EC never clears processing. Event wake classification depends on the correctness of `event_size` and host-event endianness. `cros_ec_cmd()` copies `insize` bytes back whenever the transfer succeeds, so callers must size input buffers to the expected command response.

## Test Signals
`cros_ec_proto_test.c` provides extensive KUnit coverage for v2/v3 transmit framing, protocol negotiation, no-PD passthrough behavior, legacy fallback failures, MKBP and host-sleep probing, wake-mask defaulting, transport selection, in-progress polling, EC-result mapping, event parsing, feature cache behavior, sensor-count legacy fallback, and the generic command wrapper. Transport-specific checksum and receive behavior is tested indirectly by mock transfer callbacks here and by bus driver testing elsewhere.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_proto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_proto_test.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_proto_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_proto_test_util.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_proto_test_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_proto_test_util.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_proto_test_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_rpmsg.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_rpmsg.c

## Purpose
`cros_ec_rpmsg.c` is the Chrome EC transport driver for ECs reachable over RPMsg. It adapts the generic `cros_ec_device` command callbacks to RPMsg packet exchange and converts RPMsg host-event notifications into normal Chrome EC IRQ processing.

## Important APIs, Types, and Functions
- `struct cros_ec_rpmsg_response` describes incoming RPMsg messages with a type byte and aligned payload.
- `struct cros_ec_rpmsg` stores the RPMsg device, endpoint, command completion, host-event work item, and probe/pending-event flags.
- `cros_ec_pkt_xfer_rpmsg()` sends v3 packets, waits up to 200 ms for completion, validates EC host response length and checksum, copies payload into the command, and handles reboot delay.
- `cros_ec_cmd_xfer_rpmsg()` returns `-EINVAL` because old protocol transfers are unsupported.
- `cros_ec_rpmsg_callback()` demultiplexes host-command responses and host events.
- Probe/remove/suspend/resume bind the transport into the generic Chrome EC core.

## Control Flow
Probe allocates a `cros_ec_device`, assigns `cmd_xfer`/`pkt_xfer`, creates an RPMsg endpoint, registers the EC core, then marks probe complete and drains any host event that arrived early. Command transfer prepares a v3 packet with `cros_ec_prepare_tx()`, sends it through `rpmsg_send()`, blocks on `xfer_ack`, parses `struct ec_host_response` from `ec_dev->din`, calls `cros_ec_check_result()`, validates `data_len <= insize`, computes checksum over header and data, and returns payload length. The RPMsg callback copies host-command payloads into `din` and completes the waiter; host-event messages either schedule work immediately or set a pending flag until registration completes.

## State and Persistence
Driver state is per RPMsg device and devm-managed except the endpoint, which is explicitly destroyed. `has_pending_host_event` persists only across the probe window. `probe_done` gates event handling to avoid invoking Chrome EC IRQ handling before the core registration is ready.

## Dependencies and Integration Points
It depends on Linux RPMsg, completions, workqueues, device tree match `"google,cros-ec-rpmsg"`, Chrome EC protocol helpers, and core functions `cros_ec_device_alloc()`, `cros_ec_register()`, `cros_ec_unregister()`, `cros_ec_suspend()`, `cros_ec_resume()`, and `cros_ec_irq_thread()`.

## Risks and Edge Cases
Only protocol v3 packet mode is supported, so fallback to v2 will fail. Incoming response length is truncated to `din_size` before completion, but checksum validation can still catch corrupted/truncated data. Timeout returns `-EIO`, not `-ETIMEDOUT`, which callers may treat as a generic transport failure. `has_pending_host_event` is a boolean, so multiple early host events collapse into one scheduled IRQ pass.

## Test Signals
There is no local KUnit suite for RPMsg in this subset. Useful validation comes from protocol KUnit tests for shared framing/check-result behavior and from runtime testing with RPMsg EC firmware that emits both command responses and host events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_rpmsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_sensorhub.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_sensorhub.c

## Purpose
`cros_ec_sensorhub.c` discovers motion sensors exposed by a Chrome EC and creates platform devices for the corresponding IIO sensor drivers. It also wires FIFO/ring support when the EC supports motion-sense FIFO events.

## Important APIs, Types, and Functions
- `cros_ec_sensorhub_allocate_sensor()` registers a child platform device with `struct cros_ec_sensor_platform { sensor_num }` and devm cleanup.
- `cros_ec_sensorhub_register()` loops over EC sensors, sends `MOTIONSENSE_CMD_INFO`, maps motion-sense types to platform device names, and registers sensor children.
- `cros_ec_sensorhub_probe()` allocates shared command buffers and `struct cros_ec_sensorhub`, checks EC features, retrieves sensor count, prepares FIFO support, enumerates sensors, and adds/removes ring support.
- PM callbacks disable/enable FIFO interrupts across suspend/resume.

## Control Flow
Probe obtains the parent `cros_ec_dev`, allocates a command large enough for motion-sense parameters and max EC response, and checks `EC_FEATURE_MOTION_SENSE`. In normal sensorhub mode it calls `cros_ec_get_sensor_count()`, optionally allocates ring data if `EC_FEATURE_MOTION_SENSE_FIFO` exists, enumerates every sensor with up to 50 retries on `-EBUSY`, creates typed platform children, and finally registers the FIFO notifier/ring. In legacy mode, if the EC does not advertise motion sense but the platform device exists, it creates two `"cros-ec-accel-legacy"` children.

## State and Persistence
`struct cros_ec_sensorhub` stores the EC pointer, shared command buffer, params/response aliases, sensor count, command mutex, and ring-related state allocated by `cros_ec_sensorhub_ring_allocate()`. The parent `cros_ec_dev->has_kb_wake_angle` flag is set when at least two accelerometers are found. Platform children are registered for the lifetime of the sensorhub device and devm-unregistered on teardown.

## Dependencies and Integration Points
The driver depends on Chrome EC feature and command helpers from `cros_ec_proto.c`, motion-sense command structures, `cros_ec_sensorhub_ring_*()` helpers, platform device registration, and IIO child drivers named `cros-ec-accel`, `cros-ec-gyro`, `cros-ec-mag`, `cros-ec-baro`, `cros-ec-prox`, `cros-ec-light`, `cros-ec-activity`, and `cros-ec-lid-angle`.

## Risks and Edge Cases
Sensor info retrieval tolerates individual failures by logging and continuing, so a partially enumerated sensorhub can exist. `-EBUSY` retrying handles EC sensor initialization delays but caps at 50 attempts with 5-6 ms sleeps. A zero sensor count is treated as probe failure. FIFO support must be allocated before child registration because child drivers may register callbacks. Suspend/resume behavior assumes disabling FIFO interrupts is enough to avoid unwanted EC interrupts while preserving wake signaling.

## Test Signals
No direct tests are present in this subset. Indirect test coverage exists for `cros_ec_get_sensor_count()` in `cros_ec_proto_test.c`. Runtime signals include child platform devices appearing for the expected sensor types and FIFO samples reaching registered IIO callbacks when FIFO support is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_sensorhub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_sensorhub_ring.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_sensorhub_ring.c

## Purpose
`cros_ec_sensorhub_ring.c` implements Chrome EC motion-sense FIFO processing. It registers per-sensor push callbacks, enables/disables EC FIFO interrupts, drains FIFO events from MKBP notifications, reconstructs sample timestamps across EC/AP timebases, handles batching and lost samples, and forwards samples into IIO sensor drivers.

## Important APIs, Types, and Functions
- `cros_ec_sensorhub_register_push_data()` and `cros_ec_sensorhub_unregister_push_data()` manage per-sensor callbacks.
- `cros_ec_sensorhub_ring_fifo_enable()` sends `MOTIONSENSE_CMD_FIFO_INT_ENABLE` and resets tight timestamp batch state.
- Timestamp helpers include `cros_ec_sensor_ring_median()`, `cros_ec_sensor_ring_ts_filter_update()`, `cros_ec_sensor_ring_ts_filter()`, and `cros_ec_sensor_ring_fix_overflow()`.
- `cros_ec_sensor_ring_process_event()` transforms raw EC FIFO entries into `cros_ec_sensors_ring_sample` records.
- `cros_ec_sensor_ring_spread_add()` and `_legacy()` distribute batched samples in time.
- `cros_ec_sensorhub_ring_handler()` drains FIFO data via `MOTIONSENSE_CMD_FIFO_READ`.
- `cros_ec_sensorhub_event()` is the notifier callback for `EC_MKBP_EVENT_SENSOR_FIFO`.
- `cros_ec_sensorhub_ring_allocate()`, `cros_ec_sensorhub_ring_add()`, and `cros_ec_sensorhub_ring_remove()` own allocation, notifier registration, FIFO enable, and cleanup.

## Control Flow
When `cros_ec_get_next_event()` stores a sensor FIFO MKBP event, the Chrome EC notifier calls `cros_ec_sensorhub_event()`. The notifier validates event type/size, ignores events queued during suspend, copies FIFO info and the IRQ timestamp, then calls the ring handler. The handler locks the shared command buffer, optionally refreshes FIFO info if lost samples are reported, validates count/size against the allocated ring, reads FIFO entries in chunks, converts each raw entry into an output sample, unlocks, reports lost vectors, spreads timestamps, and invokes registered per-sensor callbacks.

## State and Persistence
Ring state lives in `struct cros_ec_sensorhub`: FIFO info buffer, ring sample array, FIFO size, per-sensor push callback array, notifier block, command mutex, last/new timestamps, overflow tracking for EC sample and FIFO timestamps, optional tight-timestamp filter state, per-sensor batch state, and future-timestamp analytics counters. State persists for the platform device lifetime and is reset selectively when FIFO interrupts are toggled or ODR/lost-sample events invalidate interpolation history.

## Dependencies and Integration Points
The file depends on IIO device pointers for callback dispatch, Chrome EC motion-sense command definitions, notifier chains from the EC core, `cros_ec_get_time_ns()`, and tracepoints from `cros_ec_sensorhub_trace.h`. Sensor child drivers integrate by registering push callbacks for their sensor number.

## Risks and Edge Cases
Timestamping is the highest-risk area. The driver must translate 32-bit EC microsecond timestamps into AP nanoseconds, account for wraparound, filter IRQ latency jitter, prevent future timestamps from escaping, and spread batched samples without inventing impossible ordering. Tight timestamp spreading can drop samples when no previous batch period exists. FIFO count/size mismatches, zero reads, too many entries, or EC read errors abort the current drain. Callback registration rejects duplicate sensor slots but does not serialize with unregister beyond normal driver lifetime assumptions.

## Test Signals
There is no local unit test for the ring algorithms in this subset. Useful signals are trace events (`cros_ec_sensorhub_timestamp`, `data`, `filter`), warnings for lost/future samples, and end-to-end IIO sample delivery from EC FIFO events. The code is structured with pure-ish helpers that could be KUnit-tested for median selection, overflow correction, and timestamp spreading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_sensorhub_ring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_sensorhub_trace.h -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_sensorhub_trace.h

## Purpose
`cros_ec_sensorhub_trace.h` defines ftrace tracepoints for Chrome EC sensorhub FIFO timestamp reconstruction and sample delivery diagnostics.

## Important APIs, Types, and Functions
- `TRACE_EVENT(cros_ec_sensorhub_timestamp)` records EC sample timestamp, EC FIFO timestamp, AP FIFO IRQ timestamp, calculated current timestamp, current AP time, and delta.
- `TRACE_EVENT(cros_ec_sensorhub_data)` records sensor number and timing fields for emitted samples.
- `TRACE_EVENT(cros_ec_sensorhub_filter)` records timestamp filter deltas, median slope/error, history length, and current offsets.

## Control Flow
`cros_ec_sensorhub_ring.c` defines `CREATE_TRACE_POINTS` before including this header, so these tracepoint definitions instantiate events there. Other includes can use the header guard/multi-read pattern normally. The trace include path/file macros at the bottom are required by the kernel tracepoint generator.

## State and Persistence
The header defines tracepoint schemas, not runtime state. Trace buffers are managed by ftrace/perf infrastructure when enabled.

## Dependencies and Integration Points
It depends on Linux tracepoint infrastructure and sensorhub platform data for `struct cros_ec_sensors_ts_filter_state`. It integrates directly with the timestamp filter and sample-processing paths in `cros_ec_sensorhub_ring.c`.

## Risks and Edge Cases
Tracepoint field types must match caller argument types; mismatches can corrupt trace output or fail compilation. The header uses `TRACE_SYSTEM cros_ec`, shared with other Chrome EC tracepoints, so event names must remain unique. Format strings use signed 64-bit output for nanosecond timestamps and deltas.

## Test Signals
Compilation with tracepoints enabled is the main static signal. Runtime trace output is a diagnostic signal for timestamp jitter, future timestamps, and filter behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_sensorhub_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_spi.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_spi.c

## Purpose
`cros_ec_spi.c` is the SPI transport driver for Chrome EC. It implements both legacy command and v3 packet transfer callbacks, handles SPI framing/preamble reads, checksum validation, chip-select timing, retryable EC-not-ready markers, high-priority transfer execution, device-tree timing properties, registration with the Chrome EC core, and PM delegation.

## Important APIs, Types, and Functions
- `struct cros_ec_spi` stores the SPI device, last transfer time, start/end CS delays, and high-priority worker.
- `terminate_request()` deasserts chip select with optional delay and updates `last_transfer_ns`.
- `receive_n_bytes()`, `cros_ec_spi_receive_packet()`, and `cros_ec_spi_receive_response()` implement SPI receive phases.
- `do_cros_ec_pkt_xfer_spi()` handles protocol v3 `ec_host_response` transfers.
- `do_cros_ec_cmd_xfer_spi()` handles legacy protocol v2 response layout.
- `cros_ec_xfer_high_pri()` runs transfer work on a FIFO-scheduled kthread worker.
- Probe/remove and PM callbacks bind the transport to the generic EC core.

## Control Flow
Transfer starts with `cros_ec_prepare_tx()`, waits for the required inter-transaction recovery time, allocates an RX echo buffer, locks the SPI bus, optionally inserts a start delay, transmits the request with `cs_change`, scans returned bytes for retryable markers (`PAST_END`, `RX_BAD_DATA`, `NOT_READY`), reads the response after finding `EC_SPI_FRAME_START`, terminates the request to release CS, unlocks, then parses EC result, payload length, and checksum. Public `cmd_xfer` and `pkt_xfer` callbacks only enqueue this work on the high-priority worker and wait synchronously for completion.

## State and Persistence
Per-device state persists in `struct cros_ec_spi`: timing delays from firmware properties, `last_transfer_ns` for recovery delay enforcement, and the high-priority worker lifetime. The EC core owns command buffers and protocol state. Wakeup is enabled on the SPI device after successful registration.

## Dependencies and Integration Points
The driver depends on Linux SPI APIs, device tree compatible `"google,cros-ec-spi"`, optional DT properties `google,cros-ec-spi-pre-delay` and `google,cros-ec-spi-msg-delay`, Chrome EC protocol helpers, scheduler FIFO support, and core EC registration/suspend/resume APIs.

## Risks and Edge Cases
SPI timing is delicate: insufficient recovery, start, or end delays can make the EC abort transactions. Response polling uses a 200 ms deadline and reads 32 preamble bytes at a time. v3 packet receive checks `response->data_len > ec_dev->din_size`, but the later payload length is checked against `ec_msg->insize`; both limits matter. Legacy receive returns `-ENOSPC` for oversized payloads while v3 uses `-EMSGSIZE`. High-priority worker creation and FIFO scheduling are required to avoid long preemption during chip-select assertions.

## Test Signals
No local SPI KUnit is included in this subset. Shared protocol tests cover transmit framing and EC result handling. Runtime test signals include successful `cros_ec_register()`, absence of preamble timeouts/checksum errors, and stable command behavior under load or slow tunneled I2C commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_sysfs.c

## Purpose
`cros_ec_sysfs.c` exposes selected Chrome EC control and diagnostic functions through sysfs attributes on the EC class device: reboot control, firmware/chip/board version display, flash geometry, keyboard wake angle, USB PD mux state, and AP-driven altmode capability.

## Important APIs, Types, and Functions
- `reboot_show()` and `reboot_store()` parse reboot commands and send `EC_CMD_REBOOT_EC`.
- `version_show()` sends `GET_VERSION`, `GET_BUILD_INFO`, `GET_CHIP_INFO`, and `GET_BOARD_VERSION`.
- `flashinfo_show()` sends `EC_CMD_FLASH_INFO`.
- `kb_wake_angle_show()`/`store()` use `MOTIONSENSE_CMD_KB_WAKE_ANGLE`.
- `usbpdmuxinfo_show()` reads port count and per-port mux flags.
- `ap_mode_entry_show()` reports `EC_FEATURE_TYPEC_REQUIRE_AP_MODE_ENTRY`.
- `cros_ec_ctrl_visible()` hides attributes not applicable to a device.

## Control Flow
Probe creates an attribute group on the parent EC class device. Each sysfs read/write allocates a command buffer if needed, fills command metadata and parameters, calls `cros_ec_cmd_xfer_status()` or `cros_ec_cmd()`, formats results with `sysfs_emit*()`, and frees temporary memory. Removal deletes the attribute group. Visibility checks run when sysfs builds the group and hide keyboard wake angle unless sensor discovery found the needed accelerometers; USB PD attributes are shown only for the primary EC name.

## State and Persistence
This file stores no persistent private state. It reads and mutates EC firmware state through host commands: reboot action flags, keyboard wake angle setting, and queried status. Attribute visibility depends on `struct cros_ec_dev` fields and platform data.

## Dependencies and Integration Points
It depends on the platform driver named `"cros-ec-sysfs"`, Chrome EC command definitions, `to_cros_ec_dev()`, the generic command helpers, platform data `cros_ec_platform`, and feature state populated by protocol/sensorhub code. User space integrates through sysfs files under the EC class device.

## Risks and Edge Cases
`reboot_store()` token parsing accepts any word prefix matched by `strncasecmp()` and advances by whitespace-delimited words; ambiguous or suffixed tokens could be accepted if they start with a valid command. Version display returns partial output when later optional commands fail, embedding transfer/result errors in the text. `usbpdmuxinfo_show()` returns `-EIO` if no per-port mux reads succeed. The visibility path assumes platform data and `ec_name` are present.

## Test Signals
No local tests are present. Manual/runtime signals are sysfs attribute creation, correct hide/show behavior, successful formatted version/flashinfo reads, and expected EC behavior after reboot or keyboard wake angle writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_trace.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_trace.c

## Purpose
`cros_ec_trace.c` instantiates Chrome EC command tracepoints and defines symbolic lookup tables for EC command IDs and EC result codes.

## Important APIs, Types, and Functions
- `TRACE_SYMBOL()` maps a numeric constant to its string name.
- `EC_CMDS` is a large symbolic list of `EC_CMD_*` values used by request tracepoints.
- `EC_RESULT` maps `enum ec_status` values to names.
- Defining `CREATE_TRACE_POINTS` before including `cros_ec_trace.h` creates the tracepoint objects.

## Control Flow
This file is compiled once to instantiate tracepoints declared in `cros_ec_trace.h`. At runtime, `cros_ec_xfer_command()` emits request-start and request-done events; ftrace uses the symbolic arrays from this file to print command and result names.

## State and Persistence
No driver state is stored here. Tracepoint enablement and buffers are controlled by kernel tracing infrastructure.

## Dependencies and Integration Points
It depends on command constants from Chrome EC headers and the tracepoint definitions in `cros_ec_trace.h`. It integrates with `cros_ec_proto.c` through `trace_cros_ec_request_start()` and `trace_cros_ec_request_done()`.

## Risks and Edge Cases
The symbolic command list is generated manually from headers and can drift when new EC commands are added; unknown values will not print friendly names. The tracepoint system requires exactly one `CREATE_TRACE_POINTS` translation unit, so duplicating this pattern elsewhere for the same header would break builds.

## Test Signals
Compilation verifies symbol availability. Runtime validation is enabling `cros_ec` trace events and observing named commands/results around EC transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_trace.h -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_trace.h

## Purpose
`cros_ec_trace.h` declares the generic Chrome EC request tracepoints used around every transport transfer.

## Important APIs, Types, and Functions
- `TRACE_EVENT(cros_ec_request_start)` records command version, passthrough offset, normalized command ID, outsize, and insize.
- `TRACE_EVENT(cros_ec_request_done)` records the same fields plus EC result and Linux return value.
- `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` direct trace generation to this local header.

## Control Flow
The protocol helper calls `trace_cros_ec_request_start(msg)` immediately before the selected transport callback and `trace_cros_ec_request_done(msg, ret)` immediately afterward. The tracepoint print functions normalize passthrough commands by splitting the command into a device offset and base command ID, then use symbolic tables from `cros_ec_trace.c`.

## State and Persistence
The header defines trace schemas only. Runtime trace state is external to the driver.

## Dependencies and Integration Points
It depends on Linux tracepoint headers, Chrome EC command/protocol definitions, and the `EC_CMDS`/`EC_RESULT` symbolic macros defined before instantiation by `cros_ec_trace.c`.

## Risks and Edge Cases
The `retval` field is printed with `%u` despite being stored as signed `int`, so negative errors can display in unsigned form in trace output. Passthrough offset calculation assumes the PD passthrough offset macro is the intended divisor/modulus for all traced commands.

## Test Signals
Compile-time tracepoint generation is the static signal. Runtime signal is request-start/done trace pairs around EC commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_typec.c -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_typec.c

## Purpose
`cros_ec_typec.c` maps Chrome EC USB-C/USB-PD state into the Linux Type-C class. It registers Type-C ports from firmware-described child nodes, performs data/power role swaps through EC PD control commands, manages partner/cable/plug/altmode/PD capability objects, updates orientation/role-switch/mux/retimer state, handles EC Type-C status/discovery events, and refreshes ports on USB-PD notifications and resume.

## Important APIs, Types, and Functions
- Type-C operations: `cros_typec_enter_usb_mode()`, `cros_typec_dr_swap()`, and `cros_typec_pr_swap()`.
- Port setup helpers: `cros_typec_parse_port_props()`, `cros_typec_get_switch_handles()`, `cros_typec_register_port_altmodes()`, and `cros_typec_init_ports()`.
- Object lifecycle helpers: `cros_typec_add_partner()`, `cros_typec_remove_partner()`, `cros_typec_remove_cable()`, `cros_unregister_ports()`, and `cros_typec_unregister_altmodes()`.
- Mux/mode helpers: `cros_typec_usb_disconnect_state()`, `cros_typec_usb_safe_state()`, `cros_typec_enable_tbt()`, `cros_typec_enable_dp()`, `cros_typec_enable_usb4()`, and `cros_typec_configure_mux()`.
- Discovery/status helpers: `cros_typec_handle_sop_disc()`, `cros_typec_handle_sop_prime_disc()`, `cros_typec_register_partner_pdos()`, `cros_typec_handle_status()`, and `cros_typec_port_update()`.
- Probe/remove/PM and notifier glue: `cros_typec_probe()`, `cros_ec_typec_event()`, suspend/resume callbacks.

## Control Flow
Probe allocates `struct cros_typec_data`, finds the parent EC, queries supported `EC_CMD_USB_PD_CONTROL` version, checks EC features for Type-C status commands, mux acknowledgments, and AP-driven altmode entry, reads EC PD port count, initializes Type-C ports from child firmware nodes, performs an initial update for every port, then registers a USB-PD notifier. Notifications flush and schedule work that updates every port. Each port update queries `EC_CMD_USB_PD_CONTROL`, configures mux/retimer/role/orientation based on `EC_CMD_USB_PD_MUX_INFO`, updates Type-C role/orientation/partner state according to PD control version, and optionally handles Type-C status events from `EC_CMD_TYPEC_STATUS`.

## State and Persistence
`struct cros_typec_data` stores global driver state: EC pointer, number of ports, PD control version, feature flags, notifier, work item, and per-port pointers. Each `struct cros_typec_port` stores Type-C class objects, switch/mux/retimer/role-switch handles, current mux flags and PD role, mux state, registered port altmodes, partner/cable identities, discovery completion flags, discovery response buffer, altmode lists, and partner PD capability objects. State persists until disconnect, hard reset, driver removal, or suspend cancellation/resume refresh.

## Dependencies and Integration Points
The driver depends on ACPI/OF child port descriptions, Linux Type-C class, USB role switch, typec mux/switch/retimer APIs, USB PD VDO helpers, Chrome EC command helpers, `cros_usbpd_notify`, and local helpers in `cros_typec_vdm.h` and `cros_typec_altmode.h`. It binds to ACPI `"GOOG0014"` and OF `"google,cros-ec-typec"`.

## Risks and Edge Cases
The code must keep EC state and Type-C class objects synchronized through asynchronous notifications. Missing mux/switch/retimer/role-switch handles are logged, with `-EPROBE_DEFER` causing probe retry; later paths still call these handles when ports exist, so null/error cleanup correctness matters. Hard reset removes partner and cable state and clears the event. Discovery events are ignored once the corresponding done flag is set. Mux state updates are skipped when flags and role are unchanged. Mode setup for DP/TBT requires PD control v2 data; older ECs return `-ENOTSUPP`. Mux acknowledgment failures are warning-only.

## Test Signals
No local KUnit tests are present. Runtime signals include successful Type-C port registration, role swap behavior, partner/cable/altmode objects under sysfs, mux/retimer state changes for USB/DP/TBT/USB4, PD capability registration, and correct refresh after USB-PD notifications or resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_typec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_typec.h -->
# sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_typec.h

## Purpose
`cros_ec_typec.h` defines private data structures shared by the Chrome EC Type-C driver and related local Type-C helper modules.

## Important APIs, Types, and Functions
- The anonymous altmode enum indexes DisplayPort, Thunderbolt, USB4, and max altmode slots.
- `struct cros_typec_altmode_node` links registered `struct typec_altmode` objects in partner or plug mode lists.
- `struct cros_typec_data` stores device-global EC Type-C driver state, including EC pointer, port count, PD control version, ports array, notifier/work item, and feature flags.
- `struct cros_typec_port` stores per-port Type-C class objects, switch/mux/retimer/role-switch handles, mux state, current flags/role, identities, discovery buffers, altmode lists, partner PD capability objects, and backpointer to global data.

## Control Flow
The header does not implement control flow. `cros_ec_typec.c` allocates and populates these structures during probe, updates them from EC notifications/workqueue processing, and tears them down during disconnect or remove. Local altmode/VDM helpers use the same structures to access port state.

## State and Persistence
This header defines all long-lived state for the Type-C driver. Global state lives for the platform device lifetime. Per-port partner/cable/PD/altmode state changes dynamically as connections, hard resets, and discovery events occur.

## Dependencies and Integration Points
It depends on Linux list/notifier/workqueue APIs, Chrome EC protocol definitions, USB PD identity types, USB role switch, Type-C class, altmode, mux, and retimer APIs. It is included by `cros_ec_typec.c` and likely companion files handling VDMs and altmodes.

## Risks and Edge Cases
Because `ports` is fixed to `EC_USB_PD_MAX_PORTS`, probe clamps EC-reported port counts before filling it. The lists require proper initialization before altmode registration and proper cleanup on errors. State fields such as `mux_flags`, `role`, and discovery-done booleans are cache/coherency points between EC status and Type-C class objects.

## Test Signals
No direct tests target this header. Compile coverage from the Type-C driver and runtime creation/removal of ports, partners, cables, and altmodes exercise the structure contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/chrome/cros_ec_typec.h -->
