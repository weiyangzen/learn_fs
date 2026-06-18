# subset-b-004087 research

This grouped report covers TI FPD-Link bridge drivers, Dongwoon VCM focus drivers, and the Toshiba ET8EK8 sensor driver under `sources/distributed-fs/ceph-client/drivers/media/i2c`. Each section preserves the original source path for source-tree-aligned reconciliation.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ds90ub953.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ds90ub953.c

## Purpose
`ds90ub953.c` implements the TI DS90UB953-Q1 / DS90UB971-Q1 FPD-Link serializer as an I2C V4L2 subdevice. It bridges one local CSI-2 input to an FPD-Link output managed by a deserializer, exposes serializer GPIOs, provides a CLKOUT provider for remote sensors, and adds an I2C-ATR child adapter when a remote `i2c` node is present.

## Important APIs, Types, and Functions
`struct ub953_data` is the main state object: I2C client, regmap, optional `clkin`, GPIO chip, V4L2 subdev/pads/notifier, stream mask, indirect-register cache, CLKOUT `clk_hw`, selected mode, and `ds90ub9xx_platform_data`. Hardware access is centralized in `ub953_read()`, `ub953_write()`, `ub953_read_ind()`, and `ub953_write_ind()`. GPIO callbacks implement `get_direction`, input/output direction, `get`, `set`, and OF translation for four local GPIOs. V4L2 operations include routing/format propagation, stream enable/disable pass-through to the upstream sensor, frame-desc pass-through, and `log_status()`. Probe flows through `ub953_parse_dt()`, `ub953_hw_init()`, `ub953_gpiochip_probe()`, `ub953_register_clkout()`, `ub953_subdev_init()`, and `ub953_add_i2c_adapter()`.

## Control Flow
Probe allocates state, requires platform data from the owning deserializer, initializes regmap and locks, parses the sink CSI-2 endpoint, reads strap/mode status, validates supported sync or non-sync external-clock modes, configures CSI lane count/continuous clock/CRC, and then registers GPIO, clock, V4L2, and ATR facilities. The V4L2 graph notifier binds the remote source endpoint and creates an immutable source-to-serializer media link. Streaming is a pure pass-through: source pad stream masks are translated to sink stream masks and delegated to the upstream subdevice; active routing/format changes are rejected while streams are enabled.

## State and Persistence
State is runtime-only. `enabled_source_streams` gates active format/routing changes. `current_indirect_target` avoids repeated indirect-page writes and is protected by `reg_lock`. CLKOUT programming persists only in serializer registers until reset. There is no suspend/resume cache, filesystem state, or nonvolatile persistence.

## Dependencies and Integration Points
The driver depends on Linux regmap, GPIO, Common Clock Framework, I2C-ATR, V4L2 subdev streams, media controller links, fwnode graph parsing, and `media/i2c/ds90ub9xx.h` platform data supplied by DS90UB960-like deserializers. It imports the `I2C_ATR` namespace and matches `ti,ds90ub953-q1` and `ti,ds90ub971-q1`.

## Risks and Edge Cases
Only sync and non-sync external-clock modes are accepted; internal non-sync and DVP modes fail probe. Non-sync external mode requires `clkin`. The clock-output math depends on back-channel rate from platform data, so deserializer-provided `bc_rate` must match actual link mode. GPIO register updates sometimes use raw regmap helpers instead of `ub953_write()`, so indirect/page protection is not relevant but shared register serialization is less uniform. ATR adapter creation silently does nothing without an `i2c` child node.

## Test Signals
Useful validation signals are successful probe with both compatibles, correct CSI lane and non-continuous clock programming from DT, default and requested CLKOUT rates, GPIO direction/value operations, immutable media link creation, stream enable/disable propagation to the upstream sensor, rejection of format/routing changes while streaming, remote I2C adapter creation through ATR, and meaningful `log_status()` counters for CRC/CSI/GPIO state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ds90ub953.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ds90ub953.h -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ds90ub953.h

## Purpose
`ds90ub953.h` defines the DS90UB953/DS90UB971 register addresses and bit helpers consumed by the serializer driver and by the DS90UB960 deserializer when it configures a remote serializer over the back-channel.

## Important APIs, Types, and Functions
The header contains register constants for reset, general CSI configuration, mode selection, CLKOUT controls, I2C timing/control, local GPIO data/input control/status, CRC and CSI error reporting, indirect register access, and ID bytes. It also defines indirect register targets for pattern generator, analog, and die-ID pages plus pattern-generator and analog temperature-ramp fields. `UB971_ENH_BC_CHK` is included for UB971-specific back-channel tuning.

## Control Flow
There is no executable control flow. The constants shape control flow in `ds90ub953.c` by allowing mode validation, CSI lane programming, CLKOUT calculation writes, GPIO setup, and diagnostic reads. In `ds90ub960.c`, these constants are used to access a remote UB953/UB971 through serializer alias I2C for temperature ramp and enhanced back-channel configuration.

## State and Persistence
The header carries no state. It names volatile hardware registers whose values persist only in device register state until reset or power loss. Indirect-target constants matter because both local serializer access and deserializer-mediated serializer access must select the correct register page before reading or writing indirect data.

## Dependencies and Integration Points
It depends only on Linux bit macros via `<linux/types.h>` and is a private local include for the TI FPD-Link driver pair. The integration point is intentionally narrow: register definitions shared between the serializer driver and deserializer helper paths.

## Risks and Edge Cases
Incorrect bit definitions would affect both direct serializer configuration and remote deserializer-managed setup. The analog temperature constants are used during a serializer soft reset sequence, making bit accuracy important. Pattern-generator constants are present even though the current serializer driver does not expose a user-facing pattern generator control.

## Test Signals
Signals are indirect: successful compile of both drivers, correct mode/lane/CRC/GPIO behavior in `ds90ub953.c`, successful UB953 temperature-ramp configuration from `ds90ub960.c`, and stable diagnostic reads from defined status/error registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ds90ub953.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ds90ub960.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/ds90ub960.c

## Purpose
`ds90ub960.c` implements TI DS90UB954, DS90UB960, and DS90UB9702 FPD-Link deserializers as V4L2 media bridge subdevices. It receives up to four FPD-Link RX inputs, forwards streams to one or two CSI-2 TX outputs, configures link modes and equalization, powers remote ports, manages serializer I2C aliases through I2C-ATR, instantiates remote serializer clients, and reports link/CSI/back-channel errors.

## Important APIs, Types, and Functions
`struct ub960_data` owns chip metadata, regmap, locks, reference clock, regulators/GPIOs, delayed polling work, RX/TX port arrays, V4L2 subdev/pads/controls/notifier, stream masks, I2C-ATR, register page cache, and strobe policy. `struct ub960_rxport` holds source subdev binding, serializer fwnode/client/alias/platform data, RX/CDR mode, VPOC regulator, EQ/strobe config, and alias slot tracking. `struct ub960_txport` stores CSI lane and clock mode. Register helpers include shared, RX-paged, TX-paged, and indirect accessors. Major flows are `ub960_parse_dt_*()`, `ub960_enable_core_hw()`, `ub960_init_tx_ports()`, `ub960_init_rx_ports_ub960()`, `ub960_init_rx_ports_ub9702()`, ATR attach/detach, serializer add/remove, V4L2 routing/format/frame-desc/stream operations, and event polling.

## Control Flow
Probe initializes locks and register-page sentinels, acquires regmap/VDDIO/powerdown/refclk resources, powers and resets the deserializer, parses `links` and graph endpoints, programs CSI TX PLL/lane configuration, enables VPOC regulators, configures RX ports by chip family, creates the ATR, adds remote serializer I2C devices, registers the V4L2 subdevice, and starts a delayed polling worker. UB960/UB954 RX init programs back-channel rate, RAW/CSI mode, polarity, interrupts, serializer alias, EQ, resets, waits for stable locks, applies UB953 temperature ramp, and clears link errors. UB9702 RX init includes FPD3/FPD4 channel mode setup, back-channel driver config, auto-recovery toggling, state-machine hold/release, AEQ/DFE LMS setup, lock recovery, and final error clearing.

## State and Persistence
All state is runtime and volatile. `reg_current` caches selected RX/TX/indirect pages under `reg_lock`. `aliased_addrs` tracks active ATR alias slots per RX port under a per-port mutex. `stream_enable_mask[]` and `streaming` track active stream use and gate routing/format changes. VPOC, VDDIO, refclk, GPIO powerdown, and hardware register configuration are not persisted across remove or power loss.

## Dependencies and Integration Points
The driver depends on regmap, I2C-ATR, I2C client creation, V4L2 subdev streams, media controller links, fwnode graph parsing, MIPI CSI-2 datatypes, regulators, clocks, GPIO descriptors, delayed work, and the DS90UB953 register header. It integrates with downstream serializers through `ds90ub9xx_platform_data`, upstream camera subdevices through async notifier links, and device-tree properties such as `ti,rx-mode`, `ti,cdr-mode`, `i2c-alias`, link frequencies, data lanes, VPOC supplies, and optional EQ/strobe controls.

## Risks and Edge Cases
Interrupt support is explicitly not implemented; even if `client->irq` is present, the driver uses polling. The VC mapping is deliberately simple: one output VC per RX port per TX port and no support for sources producing multiple input VCs. RAW12 modes are parsed as unsupported. Probe fails if all requested RX links do not lock. UB9702 bring-up has many ordered analog workarounds where timing and register values are critical. `ub960_parse_dt_txports()` currently returns success even after a TX parse failure path breaks from the loop, which makes DT validation worth reviewing. Remote serializers are modeled as clients on the local adapter with aliases, a known approximation noted in comments.

## Test Signals
Key signals include successful probe for UB954/UB960/UB9702 compatibles, correct regulator/refclk/powerdown sequencing, valid TX link-frequency acceptance and CSI PLL programming, RX lock masks matching active links, ATR alias attach/detach slot programming, remote serializer client registration, media graph links for all active RX ports, stream enable/disable ordering across TX/RX/source subdevices, frame descriptor VC remapping, polling logs for link/CSI/BCC errors, and clean unwind on failures in RX init, ATR init, serializer creation, and subdev registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/ds90ub960.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/dw9714.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/dw9714.c

## Purpose
`dw9714.c` is a V4L2 lens actuator driver for the Dongwoon DW9714 voice-coil motor. It exposes a lens entity with `V4L2_CID_FOCUS_ABSOLUTE`, powers the actuator through a regulator and optional powerdown GPIO, and ramps lens position during suspend/resume to avoid abrupt motion.

## Important APIs, Types, and Functions
`struct dw9714_device` stores the V4L2 control handler, subdevice, current focus value, `vcc` regulator, and optional powerdown GPIO. `dw9714_i2c_write()` sends one big-endian 16-bit actuator command. `dw9714_t_focus_vcm()` caches the target and writes `DW9714_VAL(position, DW9714_DEFAULT_S)`. Subdev internal `open()` and `close()` hold/release runtime PM. Probe initializes power, controls, a zero-pad media entity with `MEDIA_ENT_F_LENS`, and async subdev registration.

## Control Flow
Probe acquires supplies/GPIO, powers the chip, initializes the V4L2 subdev and focus control, registers the media entity/subdevice, and enables runtime PM. Focus control writes happen synchronously through the I2C command. Suspend rounds the current value down to a 16-step boundary, walks down to zero with 1 ms delays, then powers down. Resume powers up and walks back toward the cached current value in 16-step increments.

## State and Persistence
The only persistent software state across runtime PM is `current_val`; hardware position is re-applied on resume. Power state is managed by runtime/system PM and not stored outside memory. The actuator command includes slope control bits but the driver uses a fixed default slope.

## Dependencies and Integration Points
Dependencies are I2C, regulators, GPIO descriptors, runtime PM, V4L2 controls/events, and media entity support. It matches I2C ID `dw9714` and OF compatible `dongwoon,dw9714`.

## Risks and Edge Cases
Control writes do not check runtime PM state before I2C access, so callers are expected to hold the subdev open or otherwise ensure power. Probe powers the device before registering controls, then immediately idles it with runtime PM. Suspend/resume loops log I2C failures but continue ramping, so a partial mechanical position may remain if the bus fails.

## Test Signals
Validate focus range 0-1023, big-endian I2C command encoding, regulator/GPIO sequencing, open/close runtime PM transitions, smooth suspend-to-zero and resume-to-target ramps, event/log-status control integration, and remove behavior when the device is not runtime suspended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/dw9714.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/dw9719.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/dw9719.c

## Purpose
`dw9719.c` supports several related Dongwoon VCM actuators: DW9718S, DW9719, DW9761, and DW9800K. It exposes a V4L2 lens subdevice with absolute focus control, uses CCI regmap access, configures model-specific ringing/SAC/frequency registers, and uses runtime PM autosuspend.

## Important APIs, Types, and Functions
`enum dw9719_model` selects the register map and defaults. `struct dw9719_device` stores subdev, device, CCI regmap, regulator, model, mode bits, SAC mode, VCM frequency/prescale, and focus control. `dw9719_power_up()` enables the regulator, wakes the chip from shutdown, optionally detects DW9719 vs DW9761 using the INFO register, reads optional `dongwoon,sac-mode`, deprecated `dongwoon,vcm-freq`, and `dongwoon,vcm-prescale`, then writes model-specific control registers. `dw9719_power_down()` writes shutdown before disabling the regulator. `dw9719_t_focus_abs()` writes the current register appropriate for DW9718S or the other models.

## Control Flow
Probe gets match data, initializes the CCI regmap and regulator, creates a V4L2 lens subdevice and focus control, powers up with detection/configuration so the driver works even without runtime PM, enables runtime PM with an initial usage reference, registers the subdevice, and then enables autosuspend. `s_ctrl` writes focus only if `pm_runtime_get_if_in_use()` confirms the chip is already powered. Suspend ramps focus down to zero and powers down. Resume powers up without redetecting properties and ramps back to the cached control value.

## State and Persistence
The V4L2 control value is the authoritative target focus across suspend/resume. Model, SAC, and frequency settings are stored in memory after detection/property parsing and re-applied on each power-up. No nonvolatile state is written.

## Dependencies and Integration Points
The driver depends on V4L2 CCI helpers, I2C, regulator framework, runtime PM autosuspend, V4L2 controls/subdev, and OF compatibles for each supported model. It uses `pm_sleep_ptr()` and `DEFINE_RUNTIME_DEV_PM_OPS()` for PM integration.

## Risks and Edge Cases
If runtime PM has suspended the device, focus control changes are accepted but not written until resume; this is intentional but can surprise tests expecting immediate I2C traffic. Detection is skipped for DW9718S and DW9800K because they lack INFO registers. The deprecated frequency property is still accepted with a warning. Bus errors during resume ramp power the chip back down.

## Test Signals
Test each compatible, DW9719/DW9761 INFO detection, optional SAC/prescale properties, focus write register selection, no-I2C behavior while suspended, autosuspend timing, shutdown register writes before regulator disable, and suspend/resume ramps with the final hardware focus matching the cached control.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/dw9719.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/dw9768.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/dw9768.c

## Purpose
`dw9768.c` drives Dongwoon DW9768 and Giantec GT9769 VCM lens actuators. It exposes `V4L2_CID_FOCUS_ABSOLUTE`, manages `vin` and `vdd` supplies, programs AAC ringing-control timing, and ramps the lens during runtime suspend/resume.

## Important APIs, Types, and Functions
`struct dw9768` stores bulk supplies, control handler/focus control, subdev, AAC mode, AAC timing, clock prescale, and computed movement delay. `dw9768_find_ot_multi()`, `dw9768_find_dividing_rate()`, and `dw9768_cal_move_delay()` translate DT-configurable AAC parameters into per-step delays. `dw9768_mod_reg()` performs SMBus read/modify/write. `dw9768_init()` exits powerdown, enables AAC mode, programs AAC/prescale/timing, and ramps to the current focus. `dw9768_release()` ramps down and enters powerdown. Runtime PM callbacks enable/disable regulators and call these helpers.

## Control Flow
Probe initializes the subdev, reads optional `dongwoon,aac-mode`, `dongwoon,clock-presc`, and `dongwoon,aac-timing`, computes movement delay, acquires bulk supplies, creates controls and media entity, optionally powers the device immediately for ACPI D0 or OF without PM, enables runtime PM, registers the subdev, and sets autosuspend. Focus control writes the DAC immediately via swapped-word SMBus access. Open resumes runtime PM; close schedules autosuspend.

## State and Persistence
The focus V4L2 control is the target retained across power transitions. AAC configuration and movement delay are stored in driver memory and reprogrammed after every runtime resume. Hardware register state is volatile and explicitly rebuilt.

## Dependencies and Integration Points
The driver uses I2C SMBus, regulator bulk APIs, V4L2 async/control/fwnode/subdev, media entities, runtime PM, and ACPI/OF power-state helpers. It matches `dongwoon,dw9768` and `giantec,gt9769`.

## Risks and Edge Cases
`dw9768_set_ctrl()` does not acquire runtime PM, so focus writes require the device to be powered by an open file handle or platform full-power state. Runtime suspend ignores errors from `dw9768_release()` and disables regulators regardless. DT AAC values outside the lookup tables silently fall back to default timing multipliers/dividers for delay calculation while still being written to hardware.

## Test Signals
Validate focus range 0-1023, DAC MSB/LSB SMBus encoding, regulator bulk sequencing, AAC/prescale/timing property programming, calculated movement delay, runtime resume initialization and ramp-to-focus, runtime suspend ramp-to-zero/powerdown, ACPI D0 and no-PM OF full-power paths, and cleanup after subdev registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/dw9768.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/dw9807-vcm.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/dw9807-vcm.c

## Purpose
`dw9807-vcm.c` is a V4L2 lens actuator driver for the Dongwoon DW9807 VCM. It exposes absolute focus control, polls actuator busy status before DAC writes, and ramps lens movement during runtime/system PM transitions.

## Important APIs, Types, and Functions
`struct dw9807_device` stores the V4L2 control handler, subdevice, and cached current focus. `dw9807_i2c_check()` reads the status register. `dw9807_set_dac()` polls status with `readx_poll_timeout()` until the device is not busy, then writes MSB/LSB focus bytes starting at `DW9807_MSB_ADDR`. `dw9807_set_ctrl()` caches and writes focus. PM callbacks write control register power-down/power-on values and ramp the DAC in 16-step increments.

## Control Flow
Probe allocates state, initializes the V4L2 I2C subdev and focus control, creates a zero-pad `MEDIA_ENT_F_LENS` entity, registers the async subdevice, and enables runtime PM. Open resumes the device and close releases it. Focus changes synchronously poll the status register before I2C write. Suspend ramps focus down to zero and writes CTL powerdown; resume writes CTL power-on and ramps back toward the cached focus.

## State and Persistence
`current_val` is the only remembered target across PM transitions. There are no regulators in this driver; power is controlled by the chip CTL register and any board-level dependencies outside this file. Hardware position is rebuilt by ramping after resume.

## Dependencies and Integration Points
The driver depends on raw I2C transfer helpers, `readx_poll_timeout()`, runtime PM, V4L2 controls/subdev/media entity support, and OF compatibles `dongwoon,dw9807-vcm` plus legacy `dongwoon,dw9807`.

## Risks and Edge Cases
The status poll treats `val <= 0` as ready; negative I2C errors are handled after polling, but the condition is unusual and should be tested under bus failure. There is no regulator or GPIO sequencing, so platform firmware must guarantee electrical power. The legacy compatible is retained only for old firmware and should not be used in new DTs.

## Test Signals
Check busy-poll behavior, focus range 0-1023, three-byte DAC write encoding, open/close runtime PM, suspend powerdown register write after ramp-to-zero, resume power-on register write before ramp-to-target, behavior with simulated I2C errors, and matching of both current and legacy OF compatibles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/dw9807-vcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/et8ek8/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/et8ek8/Kconfig

## Purpose
`Kconfig` declares the build-time option for the Toshiba ET8EK8 camera sensor driver.

## Important APIs, Types, and Functions
The file defines `config VIDEO_ET8EK8` as a tristate option labeled "ET8EK8 camera sensor support". Its help text identifies the device as a Toshiba 5 MP camera sensor used in the Nokia N900/RX-51.

## Control Flow
There is no runtime flow. At configuration time, enabling this symbol controls whether the ET8EK8 composite object from the local Makefile is built in, built as a module, or omitted.

## State and Persistence
The only persistent effect is the kernel configuration value. It does not define dependencies or selected symbols in this snippet, so dependency enforcement must come from surrounding media I2C Kconfig structure.

## Dependencies and Integration Points
It integrates with the media I2C driver menu and the Makefile through `obj-$(CONFIG_VIDEO_ET8EK8)`. The driver itself needs I2C, V4L2 subdev/media controller, regulators, GPIO, and clocks, but this Kconfig entry does not explicitly encode those dependencies here.

## Risks and Edge Cases
Because no explicit `depends on` clauses are present, build correctness relies on parent Kconfig context. If the file is moved or included differently, missing dependencies could surface as compile failures.

## Test Signals
Configuration tests should verify `VIDEO_ET8EK8=m` produces `et8ek8.ko`, `VIDEO_ET8EK8=y` links the object built-in, and disabling the option omits `et8ek8_mode.o` and `et8ek8_driver.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/et8ek8/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/et8ek8/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/et8ek8/Makefile

## Purpose
`Makefile` builds the ET8EK8 sensor driver as a composite object.

## Important APIs, Types, and Functions
`et8ek8-objs` is extended with `et8ek8_mode.o` and `et8ek8_driver.o`. `obj-$(CONFIG_VIDEO_ET8EK8)` adds the composite `et8ek8.o` to the kernel build when the Kconfig symbol is enabled.

## Control Flow
There is no runtime control flow. Kbuild first compiles the generated/static register-list mode object and the driver object, then links them into `et8ek8.o`.

## State and Persistence
The build recipe has no runtime state. It encodes the important link-time dependency that `et8ek8_driver.c` expects the external `meta_reglist` symbol supplied by `et8ek8_mode.o`.

## Dependencies and Integration Points
This file integrates the Kconfig symbol with kbuild and with the split ET8EK8 implementation. The driver source includes `et8ek8_reg.h`, while the mode object supplies the actual register tables declared there.

## Risks and Edge Cases
Dropping `et8ek8_mode.o` would leave `meta_reglist` unresolved. Reordering is not expected to matter for kbuild, but both objects must remain in the composite object whenever the driver is enabled.

## Test Signals
Build with `CONFIG_VIDEO_ET8EK8=m` and verify both constituent objects compile and link into `et8ek8.ko`; build with `=y` and verify no unresolved `meta_reglist`; build with the option disabled and verify no ET8EK8 objects are produced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/et8ek8/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/et8ek8/et8ek8_driver.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/et8ek8/et8ek8_driver.c

## Purpose
`et8ek8_driver.c` implements a V4L2 subdevice driver for the Toshiba ET8EK8 5 MP camera sensor. It powers the sensor, imports and selects register-list modes from `meta_reglist`, exposes format/frame-interval controls, reads OTP/private memory, and provides gain, exposure, pixel-rate, and test-pattern controls.

## Important APIs, Types, and Functions
`struct et8ek8_sensor` stores subdev, source pad, active format, reset GPIO, analog regulator, external clock, sensor revision, controls, current register list, OTP buffer, and power-count lock. I2C helpers implement 8/16-bit reads, buffered register-list writes, single writes, and delay entries. Register-list helpers select modes by type, closest format/size, and frame interval. Control helpers program analog/digital gain table values, exposure register `0x1243`, and multiple test-pattern registers. Subdev operations cover streaming, pad enumeration/format, frame intervals, power, registered/open/close, and system sleep PM.

## Control Flow
Probe acquires reset GPIO, `vana`, and legacy sensor clock, initializes the media source pad and V4L2 subdev, then registers as a sensor. The internal `registered()` callback creates the `priv_mem` sysfs file, powers the device, reads revision registers, imports/sorts the mode lists, selects the first mode, writes POWERON registers, temporarily streams to read OTP memory, powers off, and initializes controls. Opening the subdev sets a try format and increments power; closing decrements power. Starting stream writes the current mode list, applies saved control values with `v4l2_ctrl_handler_setup()`, and writes stream-on; stopping writes stream-off.

## State and Persistence
`current_reglist` and `format` are the active mode state. `power_count` reference-counts users under `power_lock`; system suspend powers down only when nonzero and resume restores power. `priv_mem` caches 128 bytes of OTP data read at registration and exposed read-only through sysfs. Control values persist in V4L2 control state while hardware is off and are applied before streaming.

## Dependencies and Integration Points
The driver depends on I2C, regulators, reset GPIO, legacy V4L2 sensor clock helpers, V4L2 controls/subdev/media entity APIs, `et8ek8_reg.h`, and the linked `et8ek8_mode.o` register tables. It matches `toshiba,et8ek8` and I2C ID `et8ek8`.

## Risks and Edge Cases
The power-on path contains a warning that reset polarity is historically misinterpreted and should not be copied. Streaming does not manage power itself; callers must have powered/opened the subdev. TRY frame interval support is explicitly missing. Register-list correctness is critical because mode programming is table-driven. OTP reads poll a status bit up to 1000 times and can delay or fail registration. `remove()` calls both `v4l2_device_unregister_subdev()` and `v4l2_async_unregister_subdev()`, which is a cleanup detail worth regression testing.

## Test Signals
Validate probe/registered initialization, revision reads for known and unknown versions, register-list import sorting, mode selection by closest format and requested frame interval, pixel-rate/exposure range updates per mode, stream-on/off register writes, saved controls applied before streaming, gain and test-pattern register programming, OTP sysfs `priv_mem` length/content, power reference counting through open/close and `s_power`, suspend/resume with active users, and builds with the paired mode object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/et8ek8/et8ek8_driver.c -->
