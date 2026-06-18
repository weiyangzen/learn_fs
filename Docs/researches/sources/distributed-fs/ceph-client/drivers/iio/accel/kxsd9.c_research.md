# sources/distributed-fs/ceph-client/drivers/iio/accel/kxsd9.c

Purpose: shared IIO implementation for the Kionix KXSD9 3-axis accelerometer and auxiliary voltage channel. It exposes raw acceleration, offset, selectable scale, mount matrix, triggered buffer capture, regulators, and runtime PM for transport wrappers.

Important APIs/types/functions: `struct kxsd9_state` holds `device`, `regmap`, mount matrix, VDD/IOVDD regulators, and cached full-scale bits. `kxsd9_common_probe()` and `kxsd9_common_remove()` are exported in namespace `IIO_KXSD9`. Raw access flows through `kxsd9_read_raw()` and `kxsd9_write_raw()`. Buffering uses `kxsd9_trigger_handler()` with `kxsd9_buffer_setup_ops`. Runtime PM is exported as `kxsd9_dev_pm_ops`.

Control flow: common probe allocates an IIO device, reads mount matrix, obtains regulators, initializes default 2g scale, powers the chip, installs a triggered buffer, registers IIO, and enables autosuspend. Raw reads resume the device, read big-endian 16-bit registers, shift to 12 valid bits, and return IIO-formatted values. Scale writes validate against the four micro-scale entries, update `CTRL_C`, and cache the selected FS bits. Power-up enables regulators, sets enable in `CTRL_B`, writes low-pass/motion/full-scale bits in `CTRL_C`, then waits 20 ms.

State and persistence: scale selection is cached in `st->scale` so power-up can restore it after runtime suspend. Hardware state is otherwise reprogrammed on resume. The triggered buffer reads X/Y/Z/AUX into a timestamp-aligned stack struct.

Dependencies and integration points: uses IIO direct mode, triggered buffers, regmap, regulators, runtime PM, mount matrix helpers, and transport wrappers from SPI/I2C files.

Risks: `pm_runtime_get_sync()` return values are ignored in raw and buffer paths. `kxsd9_common_probe()` calls `kxsd9_power_up(st)` without checking its return, so regulator or register failures can be masked until later operations. Remove cleans buffer before unregistering the IIO device, which is unusual compared with many IIO drivers and is worth regression-testing.

Test signals: scale availability and writes, raw axis/AUX reads, offset `-2048`, buffer scan mask `0x0f`, runtime autosuspend/resume restoring scale, regulator failure injection, and mount-matrix sysfs output.
