# sources/distributed-fs/ceph-client/drivers/media/i2c/video-i2c.c

Purpose: generic V4L2 video-node driver for simple I2C thermal image sensors, currently Panasonic AMG88xx Grid-Eye and Melexis MLX90640. It exposes fixed-size frame capture through videobuf2, runtime power management, AMG88xx hwmon thermistor readings, and MLX90640 EEPROM through nvmem.

Important APIs/types/functions: `struct video_i2c_chip` describes per-chip format, frame size, intervals, buffer size, bpp, regmap config, setup/xfer/power/hwmon/nvmem hooks. `struct video_i2c_data` owns V4L2 device/video_device, vb2 queue, active buffer list, capture kthread, locks, sequence, regmap, and selected frame interval. Main paths are `video_i2c_probe()`, `video_i2c_remove()`, vb2 ops `queue_setup()`, `buffer_prepare()`, `buffer_queue()`, `start_streaming()`, `stop_streaming()`, capture thread `video_i2c_thread_vid_cap()`, and ioctl ops for format/input/frame interval.

Control flow: probe allocates state, selects chip data from I2C/OF match, initializes regmap and V4L2 device, configures a vmalloc-backed capture queue, powers the chip if needed, enables runtime PM autosuspend, optionally registers hwmon/nvmem, then registers the video node. Streaming resumes PM, applies chip frame-rate setup, starts a freezable kthread, and returns queued buffers as each I2C bulk read completes. Stop kills the thread, autosuspends, and returns all pending buffers with error state.

State/persistence: frame interval, sequence number, queued buffers, and thread pointer are in-memory only. MLX90640 nvmem exposes device EEPROM contents but the driver itself does not persist settings. Runtime PM powers AMG88xx sleep/normal mode and leaves MLX90640 without chip-specific power hooks.

Dependencies/integration: integrates I2C regmap, V4L2 video_device/ioctls, vb2-vmalloc, runtime PM, kthreads/freezer, hwmon, nvmem, and OF/I2C match tables.

Risks/test signals: the capture thread drops the newest queued list entry, so queue ordering expectations should be checked. I2C read failures produce errored buffers. `s_parm` changes frame interval without an explicit streaming busy check. Tests should cover minimum two-buffer queue setup, read/mmap/userptr/dmabuf capture, frame interval clamping for both chips, AMG88xx power-on reset delays and thermistor sign handling, MLX90640 EEPROM reads, kthread stop race cleanup, and runtime PM reference balance on start failures.
