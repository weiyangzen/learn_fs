# sources/distributed-fs/ceph-client/drivers/media/i2c/s5c73m3/s5c73m3-core.c

## Purpose
`s5c73m3-core.c` implements the main Samsung S5C73M3 8 MP camera driver. It owns I2C register access, firmware/boot sequencing, sensor and output-interface subdev registration, media graph links, pad formats, frame intervals, frame descriptors, stream control, power sequencing, device-tree parsing, and module registration.

## Important APIs, Types, and Functions
The file uses `struct s5c73m3` from `s5c73m3.h` as shared state for two subdevs: a sensor subdev with ISP/JPEG source pads and an OIF subdev with two sink pads and one source pad. Register helpers are `s5c73m3_i2c_write()`, `s5c73m3_i2c_read()`, exported internal helpers `s5c73m3_write()`, `s5c73m3_read()`, and `s5c73m3_isp_command()`. Status and command helpers include `s5c73m3_check_status()`, `s5c73m3_isp_comm_result()`, `s5c73m3_system_status_wait()`, and `s5c73m3_set_af_softlanding()`.

Firmware and boot logic is in `s5c73m3_load_fw()`, `s5c73m3_read_fw_version()`, `s5c73m3_set_fw_file_version()`, `s5c73m3_get_fw_version()`, `s5c73m3_spi_boot()`, `s5c73m3_rom_boot()`, and `s5c73m3_isp_init()`. Streaming and configuration use `s5c73m3_set_frame_size()`, `s5c73m3_set_frame_rate()`, `__s5c73m3_s_stream()`, and `s5c73m3_oif_s_stream()`.

## Control Flow
Probe allocates state, parses device-tree resources, initializes two subdevs and their pads, gets six regulators, initializes controls, sets default sizes, media-bus code, frame interval, and firmware-file version, registers the companion SPI driver, briefly powers the device to read firmware identity, powers it off, and async-registers the OIF subdev. OIF registration registers the internal sensor subdev and creates immutable links from the sensor ISP/JPEG pads to the OIF sink pads.

Power-on enables supplies and clock, releases standby/reset GPIOs, then `s5c73m3_isp_init()` sets the AHB page and chooses ROM or SPI boot through module parameter `boot_from_rom`. ROM boot reads from F-ROM; SPI boot can write `SlimISP_XX.bin` over SPI and optionally update F-ROM when `update_fw` is set. Streaming serializes on `state->lock`, applies pending format/frame-interval changes, sends `COMM_SENSOR_STREAMING`, and waits for command completion.

## State and Persistence
Runtime state includes cached I2C read/write addresses, SPI device pointer, regulators/GPIOs/clock, selected sensor and OIF sizes, active source code, frame interval, frame descriptor entries, control handler, streaming/apply/ISP-ready flags, power reference count, firmware version strings, and firmware size. Persistent external state is limited to firmware loaded through the kernel firmware API and optional F-ROM update.

## Dependencies and Integration Points
The file depends on V4L2 subdev/media-entity/fwnode APIs, I2C, SPI helper functions from `s5c73m3-spi.c`, controls from `s5c73m3-ctrls.c`, regulator and GPIO frameworks, firmware loading, and a CSI-2 endpoint with four lanes. It binds as `samsung,s5c73m3`.

## Risks and Edge Cases
The power counter is manually maintained through `.s_power`. Some boot paths log SPI-not-ready but continue, and `s5c73m3_spi_boot()` does not directly propagate firmware-load failure before continuing. The OIF registration function overwrites `ret` from the first media link with the second. Several TRY-format/frame-interval comments note incomplete active-state support. Firmware version selection depends on specific characters read from the sensor.

## Test Signals
Important signals include successful probe after firmware-version read, SPI probe binding, correct ROM and SPI boot behavior, firmware load of `SlimISP_XX.bin`, optional F-ROM update completion, two-subdev media graph with immutable links, correct ISP and JPEG pad formats, frame descriptor lengths, stream-on/off command completion, AF soft-landing before final power-off, and clean resource unwinding.
