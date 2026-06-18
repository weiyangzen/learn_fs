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
