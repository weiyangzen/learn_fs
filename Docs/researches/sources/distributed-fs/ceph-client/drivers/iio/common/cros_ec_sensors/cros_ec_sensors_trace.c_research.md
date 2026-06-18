# sources/distributed-fs/ceph-client/drivers/iio/common/cros_ec_sensors/cros_ec_sensors_trace.c

Purpose: tracepoint definition unit for ChromeOS EC motion-sense host commands used by the IIO common core.

Important APIs, types, and functions: `TRACE_SYMBOL()` and `MOTIONSENSE_CMDS` provide symbolic names for motion-sense subcommands. Defining `CREATE_TRACE_POINTS` before including `cros_ec_sensors_trace.h` emits the actual tracepoint objects.

Control flow: this file is compiled into the `cros-ec-sensors-core` composite module. `cros_ec_motion_send_host_cmd()` in the core calls `trace_cros_ec_motion_host_cmd()`; the tracepoint implementation generated from this file formats events using the symbolic command table.

State and persistence: no runtime sensor state is owned here. Trace enablement and buffers are handled by the kernel tracing subsystem.

Dependencies and integration: must be linked exactly once with the trace header. The command list was generated from `include/linux/platform_data/cros_ec_commands.h`, so it depends on those enum names remaining valid.

Risks and test signals: if new motion-sense commands are added but not listed, traces print numeric fallbacks instead of useful symbols. Test signals are successful build with no duplicate tracepoint definitions and visible `cros_ec_motion_host_cmd` events under ftrace/perf when host commands are issued.
