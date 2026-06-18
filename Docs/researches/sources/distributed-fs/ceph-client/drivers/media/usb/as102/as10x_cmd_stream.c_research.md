# sources/distributed-fs/ceph-client/drivers/media/usb/as102/as10x_cmd_stream.c

## Purpose
Implements AS10x transport-stream control commands for PID filtering and firmware streaming start/stop.

## Important APIs, types, and functions
`as10x_cmd_add_PID_filter()` sends `CONTROL_PROC_SETFILTER`, writes PID, stream type, and optional filter index, then returns the firmware-assigned index. `as10x_cmd_del_PID_filter()` sends `CONTROL_PROC_REMOVEFILTER`. `as10x_cmd_start_streaming()` and `as10x_cmd_stop_streaming()` send the firmware stream enable/disable procedure IDs.

## Control flow and state
The DVB feed callbacks call add/delete PID filter when `pid_filtering` is enabled and call start/stop streaming when `ts_auto_disable` requests firmware stream control. The command functions themselves only mutate the shared bus command token and rely on the caller-held bus mutex.

## Dependencies and integration points
Integrates with `as102_drv.c` feed management, DVB demux PID filters, and USB `xfer_cmd`. Uses `struct as10x_ts_filter` from frontend type definitions.

## Risks and test signals
Risks include firmware filter capacity mismatch, index handling when caller supplies `idx >= 16`, and `as10x_cmd_stop_streaming()` storing error in `int8_t`, which can truncate transport errors. Test signals are correct demux output with hardware filtering on/off, no stale PID filters after stop, and firmware stream control working when `ts_auto_disable=1`.
