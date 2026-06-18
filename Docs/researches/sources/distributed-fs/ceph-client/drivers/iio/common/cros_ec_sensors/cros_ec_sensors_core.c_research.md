# sources/distributed-fs/ceph-client/drivers/iio/common/cros_ec_sensors/cros_ec_sensors_core.c

Purpose: shared implementation for ChromeOS EC IIO sensor drivers. It initializes EC motion-sense command state, handles FIFO or triggered-buffer setup, provides common sysfs attributes, exports host-command helpers, supports shared-memory and command data reads, pushes FIFO data into IIO buffers, and provides PM restore behavior.

Important APIs, types, and functions: `cros_ec_sensors_core_init()` allocates command buffers, queries EC command version, reads sensor info for physical devices, sets labels, default calibration scale, frequency availability, FIFO capacity, and chooses FIFO or trigger buffer setup. `cros_ec_sensors_core_register()` registers IIO and optional sensorhub push callback with cleanup. `cros_ec_motion_send_host_cmd()` marshals `param`, executes `cros_ec_cmd_xfer_status()`, emits the tracepoint, and copies responses. `cros_ec_sensors_push_data()` maps EC FIFO samples into active IIO channels. `cros_ec_sensors_read_lpc()` safely reads shared memory using busy/sample-id checks; `cros_ec_sensors_read_cmd()` uses `MOTIONSENSE_CMD_DATA`. `cros_ec_sensors_capture()` is the generic trigger handler. Core read/write helpers implement sample frequency. Ext-info exports provide calibration and sensor id.

Control flow: client probes call core init, set channels and callbacks, then call core register. Runtime host commands are serialized by each client's `cmd_lock`. FIFO-capable systems use EC push callbacks and CLOCK_BOOTTIME timestamps; older systems use software triggers.

State and persistence: core state includes command buffer/response, EC pointer, sensor number/type, calibration arrays, sign vector, frequency list, FIFO size, current range, and callbacks. EC settings persist in firmware; driver state caches values for ABI reads and resume.

Dependencies and integration: depends on ChromeOS EC proto/sensorhub APIs, IIO buffers/triggers/kfifo, tracepoint header, platform data, and exported symbols consumed by cros EC client drivers.

Risks and test signals: command-version negotiation and response size handling are central. Shared-memory reads must avoid torn samples. FIFO timestamps are adjusted when IIO clock differs. Tests should cover version 2 versus 3 frequency data, FIFO and non-FIFO paths, register cleanup, cmd_readmem safe retries, ODR zero FIFO flush, report-latency sysfs, calibration ext-info, tracepoint emission, and resume range restore.
