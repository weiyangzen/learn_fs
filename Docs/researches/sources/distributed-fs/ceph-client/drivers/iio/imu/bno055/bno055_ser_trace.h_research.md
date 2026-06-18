## sources/distributed-fs/ceph-client/drivers/iio/imu/bno055/bno055_ser_trace.h

Purpose: trace event declarations for BNO055 serial communication.

Important APIs, types, and functions: declares `TRACE_SYSTEM bno055_ser` and events `send_chunk`, `cmd_retry`, `write_reg`, `read_reg`, and `recv`. Events capture byte chunks, read/write addresses, retry count, and received buffers using dynamic arrays and formatted hex output. It sets `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE bno055_ser_trace`, then includes `trace/define_trace.h` outside the include guard.

Control flow: serial core calls `trace_send_chunk()`, `trace_cmd_retry()`, `trace_write_reg()`, `trace_read_reg()`, and `trace_recv()` around protocol activity; when tracing is disabled these compile to low overhead stubs.

State and persistence behavior: no persistent state, but traced payloads can expose raw command/data bytes useful for postmortem protocol debugging.

Dependencies and integration points: integrates Linux tracepoint macros with the serial transport and requires the companion `.c` file for instantiation.

Risks and edge cases: dynamic trace arrays copy arbitrary transfer data, so high-frequency tracing can add overhead and expose calibration/sensor register bytes in trace logs. Header path configuration is fragile without the Makefile CFLAGS.

Test signals: enable each trace event during serial reads/writes and verify chunk lengths, retry numbers, and RX bytes match observed regmap operations.
