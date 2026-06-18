# subset-b-004102 research

This grouped report covers ten V4L2 camera sensor driver files under `sources/distributed-fs/ceph-client/drivers/media/i2c`. Each section preserves the original source path so the reconciliation lane can split it into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/rj54n1cb0c.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/rj54n1cb0c.c

## Purpose
`rj54n1cb0c.c` implements the Sharp RJ54N1CB0C CMOS image sensor as an I2C V4L2 sub-device. It exposes one source pad, several media-bus formats, active-only crop and format programming, basic flip/gain/white-balance controls, sensor clock and GPIO power sequencing, and chip detection from legacy platform data.

## Important APIs, Types, and Functions
The driver state is `struct rj54n1`, which stores the `v4l2_subdev`, control handler, external clock, optional `powerup` and `enable` GPIOs, the cached I2C register bank, selected `rj54n1_datafmt`, crop/output geometry, resize coefficient, timing-generator clock, and clock-divider values. `struct rj54n1_datafmt`, `struct rj54n1_clock_div`, and `struct rj54n1_reg_val` describe format mappings, PLL/divider programming, and static register tables.

Low-level register access is through `reg_read()`, `reg_write()`, `reg_set()`, and `reg_write_multiple()`. These helpers select the high-byte register bank through register `0xff` and then use SMBus byte data operations. Geometry and mode programming is centered in `rj54n1_sensor_scale()`, `rj54n1_set_rect()`, `rj54n1_set_selection()`, `rj54n1_get_selection()`, `rj54n1_get_fmt()`, and `rj54n1_set_fmt()`. Hardware bring-up uses `rj54n1_s_power()`, `rj54n1_set_clock()`, `rj54n1_reg_init()`, `rj54n1_commit()`, `rj54n1_video_probe()`, `rj54n1_probe()`, and `rj54n1_remove()`. Controls are implemented by `rj54n1_s_ctrl()`. Optional debug register access is provided when `CONFIG_VIDEO_ADV_DEBUG` is enabled.

## Control Flow
Probe requires platform data (`struct rj54n1_pdata`) and SMBus byte-data support. It allocates state, initializes the subdev and controls, sets default full-frame geometry and YUYV format, obtains the external clock and optional GPIOs, computes `tgclk_mhz` from platform `mclk_freq`, and calls `rj54n1_video_probe()`. Video probe powers the chip, reads the two device-code registers, programs the IO polarity bit from platform data, runs control setup, then powers back down before async subdev registration.

Power-on asserts optional GPIOs, waits briefly, and enables the clock. Actual sensor register initialization is lazy: `rj54n1_set_fmt()` reads `RJ54N1_RESET_STANDBY` and calls `rj54n1_reg_init()` when the external-clock bit is not set. Initialization programs PLL/dividers, fixed-resize mode, binning levels, gain, mirror/manual-still behavior, manufacturer register tables, auto-exposure/white-balance setup, reset release, commit, firmware flag, and long fixed delays.

Format setting validates the requested bus code against `rj54n1_colour_fmts`, bounds the output size, programs output selector/byte-swap/raw alignment bits, clamps the input crop to the maximum 1:16 scale, and calls `rj54n1_sensor_scale()`. Scaling adjusts unsupported large-output ratios, writes still and preview output sizes, computes resize and skip masks, updates white-balance windows when manual windowing is used, recalculates antiflicker peak registers from `tgclk_mhz`, starts resize, and updates cached active geometry. Streaming only toggles still/preview mode through `RJ54N1_STILL_CONTROL`.

## State and Persistence
All persistent state is in the in-memory `struct rj54n1`; hardware state lives in volatile sensor registers. The driver caches the currently selected register bank and geometry but has no runtime PM state, firmware file, or filesystem persistence. Power state is implicit in caller use of `.s_power`; format programming can reinitialize the chip after power-on.

## Dependencies and Integration Points
The file depends on Linux I2C SMBus byte-data transfers, clocks, GPIO descriptors, V4L2 subdev/control/media-bus APIs, `media/i2c/rj54n1cb0c.h` platform data, and async subdev registration. It integrates with board code through legacy platform data rather than device tree, especially `mclk_freq` and `ioctl_high`.

## Risks and Edge Cases
The driver is active-format only for crop/selection and rejects TRY selection; this is older than current subdev active-state conventions. There is no lock around most state updates or register-bank caching, so concurrent control and format calls rely on higher-level serialization. The scaling algorithm contains sensor-specific prohibited resize ranges and long fixed sleeps, making regression hard without hardware. `rj54n1_s_ctrl()` writes hardware unconditionally and can fail if controls are set while the chip is powered down. Probe requires platform data, so OF-only systems cannot bind it as written.

## Test Signals
Useful signals include successful ID read `0x51:0x10`, correct clock/GPIO sequencing, SMBus bank changes without errors, successful full initialization after first active format, correct YUYV/YVYU/RGB565/raw bus-code output and byte order, stable resize/crop behavior across min/max sizes, flip/gain/auto-white-balance controls taking effect, still/preview stream toggling, and clean async registration/removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/rj54n1cb0c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/s5c73m3/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/s5c73m3/Makefile

## Purpose
This Makefile defines how the Samsung S5C73M3 camera driver is built. It combines the core I2C/V4L2 implementation, SPI firmware transport, and control implementation into one `s5c73m3` module when `CONFIG_VIDEO_S5C73M3` is enabled.

## Important APIs, Types, and Functions
The build contract is `s5c73m3-objs := s5c73m3-core.o s5c73m3-spi.o s5c73m3-ctrls.o` and `obj-$(CONFIG_VIDEO_S5C73M3) += s5c73m3.o`. There are no runtime APIs in this file, but it is the link boundary that lets `s5c73m3-core.c` call symbols exported by the local SPI and controls translation units.

## Control Flow
Kbuild compiles the three object files and links them into `s5c73m3.o`. The module entry point is the I2C driver declared in `s5c73m3-core.c`; `s5c73m3-spi.c` contributes helper registration and SPI transfer functions, and `s5c73m3-ctrls.c` contributes `s5c73m3_init_controls()`.

## State and Persistence
The file stores no runtime state. Its only persistent effect is build composition under the kernel configuration system.

## Dependencies and Integration Points
It integrates with Kconfig symbol `CONFIG_VIDEO_S5C73M3` and the Linux media I2C driver build. The object ordering means unresolved cross-file symbols must match declarations in `s5c73m3.h`.

## Risks and Edge Cases
Removing one object silently breaks link-time availability of core helper functions. Splitting the driver into multiple modules would require changing this file and the internal symbol visibility because these objects currently share one module namespace.

## Test Signals
The main signal is a successful kernel build with `CONFIG_VIDEO_S5C73M3=m` or `y`, producing a module that includes I2C probe/remove, SPI helper registration, and V4L2 control setup without unresolved symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/s5c73m3/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/s5c73m3/s5c73m3-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/s5c73m3/s5c73m3-core.c

## Purpose
`s5c73m3-core.c` implements the main Samsung S5C73M3 8 MP camera driver. It owns I2C register access, firmware/boot sequencing, sensor and output-interface subdev registration, media graph links, pad formats, frame intervals, frame descriptors, stream control, power sequencing, device-tree parsing, and module registration.

## Important APIs, Types, and Functions
The file uses `struct s5c73m3` from `s5c73m3.h` as shared state for two subdevs: a sensor subdev with ISP/JPEG source pads and an OIF subdev with two sink pads and one source pad. Register helpers are `s5c73m3_i2c_write()`, `s5c73m3_i2c_read()`, exported internal helpers `s5c73m3_write()`, `s5c73m3_read()`, and `s5c73m3_isp_command()`. Status and command helpers include `s5c73m3_check_status()`, `s5c73m3_isp_comm_result()`, `s5c73m3_system_status_wait()`, and `s5c73m3_set_af_softlanding()`.

Firmware and boot logic is in `s5c73m3_load_fw()`, `s5c73m3_read_fw_version()`, `s5c73m3_set_fw_file_version()`, `s5c73m3_get_fw_version()`, `s5c73m3_spi_boot()`, `s5c73m3_rom_boot()`, and `s5c73m3_isp_init()`. Streaming and configuration use `s5c73m3_set_frame_size()`, `s5c73m3_set_frame_rate()`, `__s5c73m3_s_stream()`, and `s5c73m3_oif_s_stream()`. Pad and interval APIs include `s5c73m3_{oif_,}get_fmt()`, `s5c73m3_{oif_,}set_fmt()`, frame-size/code enumeration, `s5c73m3_oif_get/set_frame_interval()`, and frame-desc get/set.

## Control Flow
Probe allocates state, parses device-tree resources, initializes the two subdevs and their pads, gets six regulators, initializes controls through `s5c73m3_init_controls()`, sets default ISP/JPEG sizes, media-bus code, frame interval, and firmware-file version, registers the companion SPI driver, briefly powers the device to read firmware identity, powers it off, and async-registers the OIF subdev. When the OIF subdev is registered, `s5c73m3_oif_registered()` registers the internal sensor subdev and creates immutable links from the sensor ISP/JPEG pads to the OIF sink pads.

Power-on enables all supplies, enables the clock, releases standby and reset GPIOs, then `s5c73m3_isp_init()` resets I2C address caches, sets the AHB page, and chooses ROM or SPI boot through module parameter `boot_from_rom`. ROM boot starts the MCU, waits for boot and binary-read status, remaps memory, restarts the MCU, marks ISP ready, and reads version data. SPI boot starts MCU/SPI mode, optionally writes firmware `SlimISP_XX.bin` over SPI, remaps/restarts, reads version data, and can update F-ROM when `update_fw` is set.

Streaming from the OIF serializes on `state->lock`. If pending format changes exist, it programs image output mode and frame size before sending `COMM_SENSOR_STREAMING`. Pending frame interval changes are applied after stream-on unless image stabilization is active. Format and interval setters update cached pointers and set `apply_fmt` or `apply_fiv` when not streaming; active changes while streaming are rejected for formats.

## State and Persistence
Runtime state includes cached I2C read/write addresses, SPI device pointer, regulators/GPIOs/clock, selected sensor and OIF sizes, active source code, frame interval, frame descriptor entries, control handler, streaming/apply/ISP-ready flags, power reference count, firmware version strings, and firmware size. Persistent external state is limited to firmware loaded through the kernel firmware API and optional F-ROM update triggered by module parameter.

## Dependencies and Integration Points
The file depends on V4L2 subdev/media-entity/fwnode APIs, I2C, SPI helper functions from `s5c73m3-spi.c`, controls from `s5c73m3-ctrls.c`, regulator and GPIO frameworks, firmware loading, and a CSI-2 endpoint with four lanes. It integrates with device tree compatible `samsung,s5c73m3`, I2C driver binding, and a dynamically registered SPI driver matched with the same compatible string.

## Risks and Edge Cases
The power counter is manually maintained through `.s_power`, so unbalanced callers can keep hardware on or power it off too early. Some boot paths log SPI-not-ready but continue, and `s5c73m3_spi_boot()` does not propagate `s5c73m3_load_fw()` failure directly before continuing. The OIF registration function overwrites `ret` from the first media link with the second, so an initial link failure can be lost. Several TRY-format/frame-interval comments note incomplete active-state support. Firmware version selection depends on specific characters read from the sensor.

## Test Signals
Important signals include successful probe after firmware-version read, SPI probe binding, correct ROM and SPI boot behavior, firmware load of `SlimISP_XX.bin`, optional F-ROM update completion, two-subdev media graph with immutable links, correct ISP and JPEG pad formats, frame descriptor lengths for image and embedded data, stream-on/off command completion, AF soft-landing before final power-off, and clean regulator/clock/GPIO unwinding on errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/s5c73m3/s5c73m3-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/s5c73m3/s5c73m3-ctrls.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/s5c73m3/s5c73m3-ctrls.c

## Purpose
`s5c73m3-ctrls.c` maps V4L2 controls for the S5C73M3 camera to ISP command registers. It covers focus, 3A locks, exposure metering and bias, white balance, ISO, image effects, image tuning, stabilization, JPEG quality, scene mode, flicker control, WDR, and zoom.

## Important APIs, Types, and Functions
The exported entry point is `s5c73m3_init_controls(struct s5c73m3 *state)`, which initializes `state->ctrls.handler`, creates all supported controls, clusters related controls, marks volatile controls, and assigns the handler to `state->sensor_sd`. Runtime callbacks are `s5c73m3_s_ctrl()` and `s5c73m3_g_volatile_ctrl()`.

Helper functions translate control values into `COMM_*` command values from `s5c73m3.h`: `s5c73m3_get_af_status()`, `s5c73m3_set_colorfx()`, `s5c73m3_set_exposure()`, `s5c73m3_set_white_balance()`, `s5c73m3_af_run()`, `s5c73m3_3a_lock()`, `s5c73m3_set_auto_focus()`, `s5c73m3_set_contrast()`, `s5c73m3_set_saturation()`, `s5c73m3_set_sharpness()`, `s5c73m3_set_iso()`, `s5c73m3_set_stabilization()`, `s5c73m3_set_jpeg_quality()`, `s5c73m3_set_scene_program()`, and `s5c73m3_set_power_line_freq()`.

## Control Flow
Control setup creates menu/int/std controls and then builds clusters: auto exposure with exposure bias and metering, auto ISO with manual ISO, and focus-auto with AF start/stop/status/distance. `s5c73m3_s_ctrl()` logs, locks `state->lock`, skips hardware writes when the device is powered off so values can be restored later, rejects inactive controls, and dispatches by control ID to ISP commands. `s5c73m3_g_volatile_ctrl()` rejects powered-off reads and refreshes AF status from `REG_AF_STATUS`.

Focus control selects macro/normal distance when requested, starts continuous AF or one-shot AF, stops AF on stop/manual transitions, and supports 3A focus lock by stopping or restarting AF. Exposure controls update metering and bias when cluster members are new. White balance, color effects, scene modes, ISO, JPEG quality, and power-line frequency use static lookup tables or simple range transforms before calling `s5c73m3_isp_command()`.

## State and Persistence
Control values persist in the V4L2 control handler and are applied to hardware only while powered. No filesystem state is stored. The volatile AF status control is derived from current hardware status registers. Cluster state such as `is_new`, current value, and inactive flags drives which ISP commands are emitted.

## Dependencies and Integration Points
The file depends on the shared `struct s5c73m3`, command/register constants from `s5c73m3.h`, and core helper functions `s5c73m3_read()` and `s5c73m3_isp_command()`. It integrates with the sensor subdev control handler created during I2C probe.

## Risks and Edge Cases
Many controls are silently deferred when powered off; correct restoration depends on `v4l2_ctrl_handler_setup()` after power-on in the core. `s5c73m3_g_volatile_ctrl()` switches on `V4L2_CID_FOCUS_AUTO` but updates `af_status`, which is unusual and should be covered by user-space AF status reads. Menu logging indexes use local table indexes that must remain aligned with V4L2 menu strings. Stabilization repurposes frame-rate command state and can suppress normal frame-rate programming.

## Test Signals
Useful tests include power-off control set followed by power-on restoration, AF start/stop/status transitions, 3A lock toggling AE/AWB/AF commands, exposure bias and metering cluster updates, manual/auto ISO behavior, JPEG quality thresholds, scene/effect menu mapping, stabilization frame-rate behavior, and `-EINVAL` for inactive controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/s5c73m3/s5c73m3-ctrls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/s5c73m3/s5c73m3-spi.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/s5c73m3/s5c73m3-spi.c

## Purpose
`s5c73m3-spi.c` provides the SPI transport used by the S5C73M3 core to upload firmware and perform raw SPI reads. It also registers a small SPI driver whose probe captures the matching SPI device into the shared camera state.

## Important APIs, Types, and Functions
The internal transfer primitive is `spi_xmit(struct spi_device *spi_dev, void *addr, int len, enum spi_direction dir)`, which builds a one-transfer `spi_message` for TX or RX and calls `spi_sync()`. Exported internal helpers are `s5c73m3_spi_write()`, `s5c73m3_spi_read()`, `s5c73m3_register_spi_driver()`, and `s5c73m3_unregister_spi_driver()`. `s5c73m3_spi_probe()` sets `bits_per_word = 32`, calls `spi_setup()`, and stores the probed `spi_device` under `state->lock`.

## Control Flow
The core driver calls `s5c73m3_register_spi_driver()` during I2C probe, filling `state->spidrv` with a probe callback, driver name `S5C73M3-SPI`, and OF match table `samsung,s5c73m3`. When a matching SPI device probes, the SPI callback recovers the enclosing `struct s5c73m3` from the embedded `spi_driver`, configures SPI word size, and records `state->spi_dev`.

Firmware upload calls `s5c73m3_spi_write()`, which splits the buffer into `tx_size` chunks, sends any remainder, and finally sends 32 zero padding bytes. Reads use the same chunking shape with RX transfers and no trailing padding. All actual transfer errors come from `spi_sync()`.

## State and Persistence
The file persists only the current `state->spi_dev` pointer in shared memory. There is no firmware cache, persistent SPI configuration beyond `bits_per_word`, or file state. Transfer chunk progress is local to each call.

## Dependencies and Integration Points
It depends on the Linux SPI core, device-tree matching, V4L2 logging through the shared sensor subdev, and `struct s5c73m3` from `s5c73m3.h`. It integrates tightly with `s5c73m3-core.c`, which registers/unregisters the SPI driver and calls the SPI read/write helpers during boot.

## Risks and Edge Cases
`spi_xmit()` returns `-ENODEV` if firmware upload happens before a SPI device has probed. Pointer arithmetic is performed on `void *`/`const void *`, relying on GNU C behavior used by the kernel. `s5c73m3_spi_write()` always emits 32 bytes of padding after the payload, so protocol changes must account for that trailer. The SPI driver is embedded per camera state, so multiple instances depend on the SPI core accepting those dynamically registered driver objects safely.

## Test Signals
Signals include a successful SPI probe log, `spi_setup()` accepting 32-bit words, firmware upload split into expected 64-byte chunks plus padding, clean `-ENODEV` before SPI binding, proper unregister on I2C remove or probe failure, and no `spi_sync failed` errors during ROM/SPI boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/s5c73m3/s5c73m3-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/s5c73m3/s5c73m3.h -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/s5c73m3/s5c73m3.h

## Purpose
`s5c73m3.h` is the private shared contract for the Samsung S5C73M3 driver. It defines media-bus formats, pad indexes, register-address helpers, boot/status registers, ISP command IDs and values, control/state structures, frame-size descriptors, and cross-file function prototypes.

## Important APIs, Types, and Functions
Important constants include `DRIVER_NAME`, `S5C73M3_ISP_FMT`, `S5C73M3_JPEG_FMT`, pad enums `s5c73m3_pads` and `s5c73m3_oif_pads`, `S5C73M3_REG()`, command-buffer registers `REG_CMDWR_*`, `REG_CMDRD_*`, `REG_CMDBUF_ADDR`, boot/status bits, `COMM_*` command IDs for image output, flash, autofocus, exposure, AWB, frame rate, scene, streaming, and firmware update, plus supply and default-clock constants.

`struct s5c73m3_ctrls` groups the V4L2 controls created in `s5c73m3-ctrls.c`. `struct s5c73m3_interval` maps frame-rate command values to V4L2 intervals and maximum sizes. `struct s5c73m3` is the full device state shared across core, controls, and SPI files. `struct s5c73m3_frame_size` maps supported dimensions to ISP register values. Inline helpers convert from controls or subdevs back to `struct s5c73m3`.

## Control Flow
The header shapes the whole driver state machine. Core code uses command constants for boot, stream, format, frame-rate, and firmware update commands. Control code uses the same constants to translate V4L2 controls into ISP operations. SPI code depends on the shared `struct s5c73m3` fields `spidrv`, `spi_dev`, and `lock`. The command-buffer register definitions control how `s5c73m3_read()` and `s5c73m3_write()` maintain cached 32-bit address windows over 16-bit I2C transfers.

## State and Persistence
`struct s5c73m3` is the in-memory persistence boundary: two subdevs and pad arrays, SPI and I2C handles, cached I2C addresses, regulators, GPIOs, clock, bus type, selected frame sizes, active media-bus code, frame interval, frame descriptor, mutex, controls, streaming/apply/ISP-ready bitfields, power count, firmware strings, and firmware size. The header itself stores no data.

## Dependencies and Integration Points
The header includes kernel clock/regulator/GPIO and V4L2 common/control/subdev headers. It is private to the `s5c73m3` subdirectory and links `s5c73m3-core.c`, `s5c73m3-ctrls.c`, and `s5c73m3-spi.c` through prototypes.

## Risks and Edge Cases
Because it mixes hardware register ABI, firmware command ABI, and Linux media state, changes have broad blast radius. Command numeric values must match firmware expectations; enum pad values must match media-link creation and format handlers; control grouping fields must match initialization order; and bitfield flags must remain protected by `state->lock` where core/control code expects serialization.

## Test Signals
Header validation is mainly compile and integration coverage: all three objects link, controls initialize with matching fields, media pads line up with immutable links, command constants produce successful boot/stream/control behavior, and firmware/status registers decode correctly on real hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/s5c73m3/s5c73m3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/s5k3m5.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/s5k3m5.c

## Purpose
`s5k3m5.c` implements a modern V4L2 subdev driver for the Samsung S5K3M5 raw Bayer image sensor. It configures CCI/I2C register sequences, validates a 4-lane CSI-2 endpoint and 24 MHz clock, exposes two fixed modes, supports runtime PM, and provides controls for link frequency, pixel rate, blanking, exposure, analogue gain, test pattern, and flip-dependent Bayer order.

## Important APIs, Types, and Functions
State is `struct s5k3m5`, containing device/regmap/clock/reset/regulators, one source-pad subdev, control handler, key controls, and current `struct s5k3m5_mode`. `struct s5k3m5_mode` stores width, height, HTS, VTS, default exposure, and a register-list pointer. Static register tables include `burst_array_setting`, `init_array_setting`, and per-mode arrays for 4208x3120 at 30 fps and 2104x1184 at 60 fps.

Important functions include `s5k3m5_set_ctrl()`, `s5k3m5_init_controls()`, `s5k3m5_enable_streams()`, `s5k3m5_disable_streams()`, `s5k3m5_get_format_code()`, `s5k3m5_update_pad_format()`, `s5k3m5_set_pad_format()`, enumeration/get-selection/init-state helpers, `s5k3m5_identify_sensor()`, `s5k3m5_check_hwcfg()`, `s5k3m5_power_on()`, `s5k3m5_power_off()`, `s5k3m5_probe()`, and `s5k3m5_remove()`.

## Control Flow
Probe initializes a 16-bit CCI regmap, gets and validates a 24 MHz sensor clock, parses the first fwnode endpoint for CSI-2 DPHY with exactly four data lanes and the advertised 602.5 MHz link frequency, obtains reset GPIO and four supplies, powers on to read chip ID `0x30d5`, initializes controls, sets subdev state operations and media entity, finalizes the subdev, enables runtime PM, registers the sensor subdev, then enables autosuspend.

Stream-on resumes runtime PM, writes page/version registers, delays, applies burst/init/mode CCI sequences, runs `__v4l2_ctrl_handler_setup()`, and writes `S5K3M5_REG_CTRL_MODE` with streaming plus H/V flip bits. Stream-off writes zero to the same control register and autosuspends. Format selection chooses the nearest supported mode, updates hblank/vblank/exposure ranges when active mode changes, and stores the resulting try/active pad format. Bayer media-bus code is derived from H/V flip values.

## State and Persistence
State is in memory only: current mode, control values, runtime PM status, reset line, regulator state, and volatile sensor registers. There is no firmware or filesystem persistence. Controls set while the device is suspended update cached V4L2 values and are applied at stream-on.

## Dependencies and Integration Points
The driver depends on V4L2 CCI helpers, V4L2 controls/subdev/fwnode APIs, runtime PM, regulators, GPIO, clock framework, and OF compatible `samsung,s5k3m5`. It integrates with media pipelines as a single-source-pad camera sensor using `v4l2_async_register_subdev_sensor()`.

## Risks and Edge Cases
The large register arrays are opaque sensor programming; ordering errors can prevent stream start. H/V flip controls return success without immediate register writes and are only applied in the stream control word, so changing flip while streaming may not take effect until restart. `get_selection()` sets height to `mode->width`, which looks like a width/height typo for crop bounds. Hardware config validation computes a link-frequency bitmap but only returns the helper result; boards must provide the exact supported link frequency.

## Test Signals
Signals include successful 24 MHz clock validation, endpoint lane/link-frequency acceptance, chip ID read, runtime PM autosuspend/resume, stream-on with all CCI sequences written, correct 4208x3120 and 2104x1184 format selection, updated VBLANK/exposure limits, Bayer code changes for each flip combination, test-pattern register writes, and clean removal from suspended and active states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/s5k3m5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/s5k5baf.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/s5k5baf.c

## Purpose
`s5k5baf.c` implements the Samsung S5K5BAF UXGA sensor with embedded SoC ISP. It exposes a CIS subdev and an ISP subdev, parses optional setfile firmware sequences, programs a banked 16-bit I2C command interface, controls power/GPIO/clock/resources, manages crop/compose/output configuration, supports MIPI CSI-2 or parallel output, and maps V4L2 controls into firmware registers.

## Important APIs, Types, and Functions
Core state is `struct s5k5baf`, which stores GPIOs, bus type/lane count, regulators, clock, optional parsed `struct s5k5baf_fw`, CIS and ISP subdevs, pads, mutex, error latch, crop/compose rectangles, pixel-format index, frame intervals, cached auto-algorithm register, control groups, streaming/apply flags, and power count. Register and firmware helpers include `s5k5baf_fw_parse()`, `s5k5baf_i2c_read()`, `s5k5baf_i2c_write()`, `s5k5baf_read()`, `s5k5baf_write()`, `s5k5baf_write_arr_seq()`, `s5k5baf_write_nseq()`, `s5k5baf_synchronize()`, and `s5k5baf_fw_get_seq()`.

Hardware setup functions include `s5k5baf_hw_patch()`, `s5k5baf_hw_set_clocks()`, `s5k5baf_hw_set_ccm()`, `s5k5baf_hw_set_cis()`, `s5k5baf_hw_set_video_bus()`, `s5k5baf_hw_set_config()`, `s5k5baf_hw_set_crop_rects()`, `s5k5baf_hw_validate_cfg()`, `s5k5baf_hw_find_min_fiv()`, `s5k5baf_hw_set_stream()`, and control-specific `s5k5baf_hw_set_*()` helpers. Subdev operations cover frame intervals, formats, selection rectangles, streaming, power, registration, and controls.

## Control Flow
Probe parses the OF endpoint to determine parallel vs CSI-2 and lane count, configures the CIS and ISP media entities, obtains mandatory standby/reset GPIOs, regulators, and clock, powers on briefly to initialize the command interface and verify firmware API version, powers off, initializes controls, and async-registers the ISP subdev. On ISP registration, the driver registers the internal CIS subdev and creates an immutable CIS-to-ISP media link.

Power-on optionally loads `s5k5baf-cfg.bin` once, resets cached geometry/control state, enables regulators and clock, releases GPIOs, initializes command pages, applies firmware patch sequences, signals host interrupt, programs clocks, output bus, CIS tuning, and color correction matrices, then sets up controls. Streaming applies output config, crop rectangles, frame interval validation, enables preview, and writes one extra undocumented register. Stream-off disables preview.

Selection state models a pipeline from fixed CIS bounds through sink crop, compose scaling, and source crop. Set-selection bounds and aligns rectangles, marks crop application when the pipeline differs from full sensor, and can apply crop live while preserving output dimensions. Format handling fixes CIS format and bounds ISP output to supported YUV/RGB formats.

## State and Persistence
The driver uses an error latch (`state->error`) for batched register operations; once set, later register helpers no-op until `s5k5baf_clear_error()`. Parsed setfile firmware is devm-allocated and retained for the device lifetime. Runtime state persists in memory across power cycles but is reinitialized on power-on for defaults. Hardware registers are volatile.

## Dependencies and Integration Points
Dependencies include V4L2 media/subdev/control/fwnode APIs, firmware loading, I2C, clock, GPIO, regulator, OF graph parsing, and optional firmware file `s5k5baf-cfg.bin`. The driver binds to `samsung,s5k5baf` and creates a two-subdev media topology.

## Risks and Edge Cases
The setfile parser validates offsets but trusts the sequence format consumed by `s5k5baf_write_nseq()`. Error-latch semantics simplify batch writes but can hide the first failing operation until a later clear. Several register sequences are undocumented and derived from vendor code. `s5k5baf_hw_set_mirror()` appears to use `vflip` for both bits rather than combining hflip and vflip. `enum_frame_size()` assigns min/max height in reversed-looking order for the ISP path. Firmware absence is warned about but not fatal, so behavior may vary by board tuning.

## Test Signals
Signals include firmware API version log, optional setfile parse success, correct media graph with CIS and ISP subdevs, clock/PLL configuration without `REG_I_ERROR_INFO`, CSI-2 lane packet setup, stream-on/off preview control, crop/compose/source selection behavior, frame interval validation and recovery from `CFG_ERROR_RANGE`, V4L2 control effects for AWB/AE/flicker/color/test pattern, and correct cleanup of both media entities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/s5k5baf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/s5k6a3.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/s5k6a3.c

## Purpose
`s5k6a3.c` is a small V4L2 subdev driver for the Samsung S5K6A3 raw image sensor. It exposes one source pad with a fixed 10-bit Bayer media-bus format, bounds frame dimensions, and provides simple manual power sequencing through regulators, clock, reset GPIO, and runtime PM no-callback accounting.

## Important APIs, Types, and Functions
Driver state is `struct s5k6a3`, containing device, subdev, source pad, three regulators, reset GPIO, mutex, active `v4l2_mbus_framefmt`, clock, and `power_count`. Format functions are `s5k6a3_enum_mbus_code()`, `s5k6a3_try_format()`, `__s5k6a3_get_format()`, `s5k6a3_set_fmt()`, `s5k6a3_get_fmt()`, and `s5k6a3_open()`. Power functions are `__s5k6a3_power_on()`, `__s5k6a3_power_off()`, and `s5k6a3_s_power()`. Probe/remove handle resource acquisition and async subdev registration.

## Control Flow
Probe allocates state, gets a legacy sensor clock named `extclk` with 24 MHz default, obtains a reset GPIO initially high, bulk-gets `svdda`, `svddio`, and `afvdd`, initializes the I2C subdev, sets default 1296x732 Bayer format, initializes the media source pad, enables runtime PM without callbacks, and registers the subdev. Opening a file handle seeds TRY state with the default format.

Format setting clamps width and height between 32 and 1412 pixels and forces `MEDIA_BUS_FMT_SGRBG10_1X10`, no field. Active and TRY formats share the same helper but are protected by the state mutex. Power-on increments runtime PM, enables the analog supply first, enables the clock, then enables the remaining supplies, toggles reset high/low with short delays, and waits 20 ms for sensor initialization. Power-off asserts reset, disables supplies in reverse order, disables the clock, and puts runtime PM. `.s_power` reference-counts transitions.

## State and Persistence
The only persistent state is in memory: active format and `power_count`. There are no sensor register tables, controls, firmware files, or persistent hardware settings in this driver. Runtime PM is used only as an accounting wrapper because no callbacks are installed.

## Dependencies and Integration Points
The driver depends on V4L2 async/subdev APIs, media entity pads, regulator bulk APIs, GPIO descriptors, clocks, I2C binding, and optional OF compatible `samsung,s5k6a3`. It integrates as a single camera sensor source pad.

## Risks and Edge Cases
There is no chip-ID verification, stream operation, or register programming; board firmware or a companion controller may be expected to configure the sensor. `__s5k6a3_power_on()` calls `pm_runtime_get()` and must pair all error paths correctly with `pm_runtime_put()`. The empty I2C ID table relies on OF matching for practical binding. Active format changes are allowed regardless of power state and have no direct hardware effect.

## Test Signals
Signals include successful resource acquisition, async subdev registration, correct default TRY and active formats, bounded format dimensions, balanced `.s_power` reference counting, regulator/clock/reset sequencing on a scope or board logs, and clean remove after runtime PM disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/s5k6a3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/s5kjn1.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/s5kjn1.c

## Purpose
`s5kjn1.c` implements a V4L2 subdev driver for the Samsung S5KJN1 raw Bayer sensor. It uses V4L2 CCI register helpers, validates a 4-lane CSI-2 endpoint and 24 MHz MCLK, exposes 4080x3072 and 8160x6144 modes, manages optional regulators with runtime PM, and supports exposure, gain, blanking, test pattern, and flip-dependent Bayer order controls.

## Important APIs, Types, and Functions
State is `struct s5kjn1`, with device/regmap/clock/reset, optional `afvdd`, `vdda`, `vddd`, and `vddio` regulators, one source-pad subdev, control handler, cached controls, and current `struct s5kjn1_mode`. Modes store width, height, HTS, VTS, default exposure, mode-specific exposure margin, and a register list. Register tables include `init_array_setting`, `s5kjn1_4080x3072_30fps_mode`, and `s5kjn1_8160x6144_10fps_mode`.

Important functions mirror the S5K3M5 pattern: `s5kjn1_set_ctrl()`, `s5kjn1_init_controls()`, `s5kjn1_enable_streams()`, `s5kjn1_disable_streams()`, format/enumeration/selection/init-state helpers, `s5kjn1_identify_sensor()`, `s5kjn1_check_hwcfg()`, `s5kjn1_power_on()`, `s5kjn1_power_off()`, `s5kjn1_probe()`, and `s5kjn1_remove()`.

## Control Flow
Probe creates a 16-bit CCI regmap, validates 24 MHz clock, parses the first fwnode endpoint for CSI-2 DPHY with exactly four lanes and supported 700 MHz link frequency, obtains reset GPIO, optionally obtains four regulators, powers the device to read chip ID `0x38e1`, initializes controls, finalizes the media entity and subdev state, enables runtime PM, registers the sensor subdev, and arms autosuspend.

Stream-on resumes runtime PM, writes page/version/reset staging registers, waits, applies common init and selected mode tables, applies cached controls, and writes `S5KJN1_REG_CTRL_MODE` to start streaming. Stream-off writes zero and autosuspends. Control writes while active program analogue gain, exposure, VTS, orientation, and test pattern registers; when suspended they only update cached control values. Format setting picks the nearest supported mode, updates hblank/vblank/exposure ranges based on the mode's exposure margin, and stores the pad format. Bayer order is computed from current H/V flip controls.

## State and Persistence
The file has no firmware or filesystem state. Runtime state consists of current mode, controls, regulator/clock/reset state, runtime PM state, and volatile sensor registers. Optional regulators allow boards to omit named supplies, with power sequencing adapting to the available set.

## Dependencies and Integration Points
Dependencies include Linux CCI/regmap over I2C, V4L2 controls/subdev/fwnode APIs, runtime PM, clock, GPIO, optional regulators, OF compatible `samsung,s5kjn1`, and media graph registration as a sensor source subdev.

## Risks and Edge Cases
The register tables are large and opaque, so mode timing changes require hardware validation. `get_selection()` reports height as `mode->width`, which appears to be a crop rectangle typo. Link-frequency validation requires the endpoint to advertise exactly a supported frequency. Optional regulators make the driver flexible but can mask incomplete board descriptions until power sequencing fails electrically. Unlike S5K3M5, flip controls are written to an orientation register when active, so Bayer-code changes and streaming orientation must remain synchronized.

## Test Signals
Signals include successful optional-regulator handling, chip ID match, endpoint lane/link-frequency validation, stream-on after common and mode register sequences, 4080x3072 and 8160x6144 mode switching, correct exposure range updates from per-mode margins, active orientation writes on H/V flip, Bayer-code enumeration changes, runtime PM autosuspend, and clean removal from active or suspended states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/s5kjn1.c -->
