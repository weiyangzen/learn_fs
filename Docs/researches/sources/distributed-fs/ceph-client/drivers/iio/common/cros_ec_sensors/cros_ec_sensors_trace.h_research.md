# sources/distributed-fs/ceph-client/drivers/iio/common/cros_ec_sensors/cros_ec_sensors_trace.h

Purpose: trace event declaration header for ChromeOS EC IIO sensor host-command tracing.

Important APIs, types, and functions: `TRACE_EVENT(cros_ec_motion_host_cmd, ...)` records the motion-sense command id, sensor id, data field, transfer return value, and response return field. `TP_printk` uses `__print_symbolic(..., MOTIONSENSE_CMDS)` to render command names. The bottom of the file sets `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` for `trace/define_trace.h`.

Control flow: normal includes declare the tracepoint; the companion `.c` file defines `CREATE_TRACE_POINTS` and includes this header to instantiate it. The core invokes the tracepoint after every EC motion host command transfer.

State and persistence: no driver state is stored. Trace records are transient tracing subsystem data.

Dependencies and integration: includes platform EC command/proto definitions and Linux tracepoint headers. It relies on `MOTIONSENSE_CMDS` being defined by the including C file before trace generation.

Risks and test signals: field extraction currently uses `param->sensor_odr` members for sensor id/data, which is most meaningful for ODR commands and may be less descriptive for other subcommands. Tests should verify trace compilation, trace output formatting for several subcommands, and no include-path breakage after source tree moves.
