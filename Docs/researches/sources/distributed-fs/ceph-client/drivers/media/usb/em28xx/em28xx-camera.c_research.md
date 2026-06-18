# sources/distributed-fs/ceph-client/drivers/media/usb/em28xx/em28xx-camera.c

## Purpose
`em28xx-camera.c` detects and initializes image sensors attached to em28xx webcam-style bridges. It probes known Micron/Aptina and OmniVision I2C addresses, records the detected sensor type in `dev->em28xx_sensor`, and configures the V4L2 bridge state and sensor subdevice setup for supported sensors.

## Important APIs, Types, and Functions
The exported entry points are `em28xx_detect_sensor()` and `em28xx_init_camera()`. Sensor probing is handled by `em28xx_probe_sensor_micron()` and `em28xx_probe_sensor_omnivision()`, using address arrays `micron_sensor_addrs[]` and `omnivision_sensor_addrs[]`. Two legacy direct-initialization helpers, `em28xx_initialize_mt9m111()` and `em28xx_initialize_mt9m001()`, write hardcoded register sequences without creating proper media graph sensor entities. Supported `enum em28xx_sensor` values visible here are `EM28XX_MT9V011`, `EM28XX_MT9M001`, `EM28XX_MT9M111`, and `EM28XX_OV2640`.

## Control Flow
`em28xx_detect_sensor()` first probes Micron-style sensors. The Micron path iterates candidate I2C addresses, reads a 16-bit chip ID at register `0x00`, reads it again from `0xff` for validation, byte-swaps SMBus little-endian data, and maps known IDs to sensor names and selected driver support. If no supported Micron sensor is found, the OmniVision path iterates its candidate addresses, verifies manufacturer ID `0x7fa2` from registers `0x1c/0x1d`, reads product ID from `0x0a/0x0b`, and maps known products, with `OV2640` being the supported initialized sensor in this file.

`em28xx_init_camera()` switches on `dev->em28xx_sensor`. For `MT9V011`, it sets 640x480 geometry, lowers bridge XCLK to 4.3 MHz, passes `mt9v011_platform_data` to `v4l2_i2c_new_subdev_board()`, and configures RGB Bayer bridge input. For `MT9M001` and `MT9M111`, it sets sensor dimensions, writes hardcoded initialization sequences, and configures bridge input mode. For `OV2640`, it creates an SCCB I2C V4L2 subdevice, sets the active pad format to 640x480 YUYV, sets bridge XCLK to 24 MHz, and selects YUV422 bridge input. Unknown or unsupported sensors return `-EINVAL`.

## State and Persistence Behavior
The detection result is stored in `dev->em28xx_sensor`, while video geometry and bridge input settings are stored in `dev->v4l2->sensor_xres`, `sensor_yres`, `sensor_xtal`, `vinmode`, and `vinctl`. The helper also mutates `client->addr` on `dev->i2c_client[dev->def_i2c_bus]` while scanning. State is runtime-only; no firmware or persistent storage is updated. Sensor register writes during initialization alter attached hardware state until reset, suspend, or disconnect.

## Dependencies and Integration Points
This file depends on em28xx I2C bus setup from `em28xx-cards.c`, bridge register writes from `em28xx-core.c`, V4L2 subdevice registration, and sensor-specific media drivers such as `mt9v011` and `ov2640`. It is called from board setup when the board can be a webcam and from V4L2 initialization paths that need camera geometry and bridge format. It also relies on constants from `em28xx.h` and media bus format definitions.

## Risks and Edge Cases
The Micron and OmniVision scanners mutate a shared `i2c_client` address, so callers must not assume the original address survives detection. Several detected sensors are reported as unsupported and leave `EM28XX_NOSENSOR`; only a subset has initialization paths. The `MT9M001` and `MT9M111` helpers are explicitly FIXME-level code and do not create sensor entities in the media graph. Sensor detection relies on ID reads that can be affected by bus speed, reset GPIO state, and SCCB quirks. The OV2640 path hardcodes VGA output even though the chip can support higher resolutions, and the comments describe missing clock/output-format switching for larger modes.

## Test Signals
Build coverage should include the em28xx webcam path plus `CONFIG_VIDEO_MT9V011` and `CONFIG_VIDEO_OV2640` combinations. Runtime signals include probe logs identifying the expected sensor, successful creation of the appropriate V4L2 subdevice where supported, bridge XCLK writes matching the sensor, a usable 640x480 stream for MT9V011/OV2640, and graceful `-ENODEV`/`-EINVAL` behavior when no sensor or an unsupported sensor is present. Media graph inspection should reveal the known gap for legacy direct-initialized sensors.
