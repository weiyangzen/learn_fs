# `sources/distributed-fs/ceph-client/include/linux/iio/common/cros_ec_sensors_core.h`

Purpose: shared ChromeOS EC sensor-hub IIO core state and helper APIs for motion sensors exposed through EC host commands or LPC.

Important APIs/types/functions: axis enum, sample size constants, `cros_ec_sensors_capture_t`, `struct cros_ec_sensors_core_state`, read functions for LPC/command paths, core init/register, trigger capture, push data, host command sender, read/read_avail/write helpers, PM ops, and ext-info arrays.

Control flow and state: persistent state owns EC pointer, command mutex, command message/param/response buffers, motion sensor type, range/calibration/sign state, aligned sample buffer, selected read function, FIFO size, and frequency table. Read/write paths send EC host commands under lock; triggered capture pushes calibrated samples and timestamp.

Dependencies/integration: depends on IIO, IRQ return types, ChromeOS EC command/proto/sensorhub platform data, and platform devices.

Risks: EC command serialization via `cmd_lock` is mandatory; range changes must be re-applied on resume; sample buffer has fixed sizing and timestamp alignment assumptions; FIFO frequency tables must match EC firmware.

Test signals: LPC and command read paths, triggered capture/push data, range/calibration read/write, available frequency reporting, suspend/resume PM ops, FIFO event handling, and EC command failure paths.
