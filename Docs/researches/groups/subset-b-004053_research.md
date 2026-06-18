# subset-b-004053 Research

Research scope: DVB frontend build metadata and selected A8293, AF9013, AF9033, AS102, ASCOT2E, ATBM8830, and AU8522 source files under `sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/Kconfig

## Purpose
This Kconfig file defines the configurable build surface for DVB frontend drivers when `MEDIA_DIGITAL_TV_SUPPORT` is enabled. It organizes demodulators, tuners, SEC controllers, Common Interface devices, and test-only frontends into the `Customise DVB Frontends` menu, while allowing ancillary subdrivers to be hidden by `MEDIA_HIDE_ANCILLARY_SUBDRV`.

## Important APIs, Types, And Build Contracts
The file exports Kconfig symbols rather than C APIs. For this work item, the important symbols are `DVB_A8293`, `DVB_AF9013`, `DVB_AF9033`, `DVB_AS102_FE`, `DVB_ASCOT2E`, `DVB_ATBM8830`, `DVB_AU8522`, `DVB_AU8522_DTV`, and `DVB_AU8522_V4L`. Most visible frontend symbols are `tristate` and default to module builds when `MEDIA_SUBDRV_AUTOSELECT` is disabled. Dependencies express runtime subsystem requirements, typically `DVB_CORE && I2C`, with extra requirements such as `I2C_MUX` for AF9013 and `VIDEO_DEV` for AU8522 analog/V4L support. `DVB_AF9013` selects `REGMAP`; `DVB_AF9033` selects `REGMAP_I2C`; AU8522 DTV and V4L variants select the hidden common `DVB_AU8522`.

## Control Flow And Integration
Kconfig does not execute device logic, but it drives compilation and module availability. `DVB_AS102_FE` is hidden and defaults to `DVB_AS102`, so the USB/device parent selects the frontend automatically. AU8522 splits common support from DTV and analog decoder modules: `DVB_AU8522_DTV` and `DVB_AU8522_V4L` select common state/register helpers. The file also sources nested Kconfig files for subdirectories such as `cxd2880` and `drx39xyj`.

## State, Persistence, And Dependencies
Configuration state persists in the kernel build `.config`. Build-time dependencies protect against missing I2C, DVB core, regmap, I2C mux, or V4L2 infrastructure. There is no runtime persistence.

## Risks
Incorrect dependencies can build drivers without required helper subsystems or hide attach stubs unexpectedly. The AU8522 split is especially sensitive: common helpers must be present when either DTV or V4L modules are enabled. `DVB_AF9033` advertises many clocks in its public header, but the implementation in this tree currently rejects clocks other than 12 MHz at probe, so Kconfig alone does not describe all runtime constraints.

## Test Signals
Useful validation is configuration matrix testing: `allyesconfig`, `allmodconfig`, and targeted module builds for each symbol. Probe-path tests need matching hardware or emulated I2C/regmap coverage; Kconfig validation should confirm selected dependencies appear in generated `.config`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/Makefile

## Purpose
This Makefile maps DVB frontend Kconfig symbols to kernel objects and subdirectories. It is the compilation index for the `drivers/media/dvb-frontends` directory.

## Important APIs, Types, And Build Contracts
The relevant object mappings are `CONFIG_DVB_A8293 -> a8293.o`, `CONFIG_DVB_AF9013 -> af9013.o`, `CONFIG_DVB_AF9033 -> af9033.o`, `CONFIG_DVB_AS102_FE -> as102_fe.o`, `CONFIG_DVB_ASCOT2E -> ascot2e.o`, `CONFIG_DVB_ATBM8830 -> atbm8830.o`, `CONFIG_DVB_AU8522 -> au8522_common.o`, `CONFIG_DVB_AU8522_DTV -> au8522_dig.o`, and `CONFIG_DVB_AU8522_V4L -> au8522_decoder.o`. The file adds `drivers/media/tuners/` to the include path for all objects and conditionally adds the DVB USB v2 include path for `CONFIG_DVB_RTL2832_SDR`.

## Control Flow And Integration
The build is flat for most drivers, with a few multi-object composites such as `cxd2820r`, `drxd`, `drxk`, `stb0899`, and `stv0900`. Entries are intended to remain sorted by Kconfig name. AU8522 demonstrates shared-object integration: common state helpers are compiled under `DVB_AU8522`, while the digital and analog entry points compile under separate Kconfig symbols.

## State, Persistence, And Dependencies
The Makefile has no runtime state. Its persistent effect is the generated object/module set selected by `.config`. The include-path choices affect all source files in the directory, so headers from tuner drivers are intentionally available.

## Risks
Missing object mappings make valid Kconfig symbols ineffective. Unsorted additions violate the local maintenance rule and can cause review churn. AU8522 object separation can break at link/load time if exported helpers in `au8522_common.o` are not built before either DTV or V4L consumers.

## Test Signals
Run targeted `make M=drivers/media/dvb-frontends` or full kernel module builds for the selected configs. Link errors around `au8522_*`, `af9013_*`, or `af9033_*` symbols are strong integration signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/a8293.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/a8293.c

## Purpose
`a8293.c` implements an I2C client driver for the Allegro A8293 satellite equipment control power device. It supplies DVB frontend `set_voltage` support for LNB voltage control.

## Important APIs, Types, And Functions
`struct a8293_dev` stores the `i2c_client`, a two-byte cached register image, and the configured slew rate. `a8293_probe()` consumes `struct a8293_platform_data`, reads the device to confirm it responds, overrides `fe->ops.set_voltage`, and stores private state in `fe->sec_priv`. `a8293_set_voltage()` dispatches to `a8293_set_voltage_slew()` when `volt_slew_nanos_per_mv` is positive and below 1600, otherwise to `a8293_set_voltage_noslew()`. The module registers a normal `i2c_driver` named `a8293`.

## Control Flow
Voltage changes translate DVB `SEC_VOLTAGE_OFF`, `SEC_VOLTAGE_13`, and `SEC_VOLTAGE_18` into A8293 register values. The slew path first reads status to clear stale faults, infers the previous voltage from the cached register, then increments through known millivolt steps with `usleep_range()` delays. Both paths program `reg1 = 0x82` for tone gate/mode after voltage selection.

## State And Persistence
Runtime state is the heap-allocated `a8293_dev`, cached register bytes, and `fe->sec_priv`. State is not persisted across driver unload or reprobe. The register cache is advisory and can diverge if hardware resets outside driver control.

## Dependencies And Integration Points
The driver depends on I2C and DVB frontend core types. It integrates by mutating an already-created DVB frontend supplied by platform data. There is no OF/ACPI match table in this file, only I2C device ID `"a8293"`.

## Risks
`a8293_set_voltage()` ignores return values from its helper paths and always returns zero, hiding I2C failures from callers. Probe assumes `client->dev.platform_data` and `pdata->dvb_frontend` are valid. The slew implementation relies on cached `dev->reg[0]` for previous voltage, which is zeroed at allocation and not initialized from hardware state.

## Test Signals
Hardware tests should exercise OFF/13V/18V transitions with and without slew. Fault injection around `i2c_master_send()` and `i2c_master_recv()` should expose the currently masked helper failure in `a8293_set_voltage()`. Kernel logs should include successful attach and debug failures when dynamic debugging is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/a8293.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/a8293.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/a8293.h

## Purpose
This public header defines the platform contract for the Allegro A8293 SEC driver.

## Important APIs And Types
`struct a8293_platform_data` carries a target `struct dvb_frontend *dvb_frontend` and `int volt_slew_nanos_per_mv`. The comments document supported I2C addresses `0x08` through `0x0b`. The header includes `<media/dvb_frontend.h>` for DVB frontend declarations.

## Control Flow And Integration
Board or parent drivers instantiate the I2C client with this platform data. At probe, `a8293.c` uses the frontend pointer to install `set_voltage` and uses the slew parameter to choose direct versus ramped voltage changes. This header exposes no attach wrapper; integration is via the I2C driver model and platform data.

## State And Persistence
The header declares input configuration only. Runtime state lives in `a8293.c` after probe.

## Dependencies
Consumers must be in-kernel media/DVB code with access to `struct dvb_frontend`. The matching Kconfig symbol depends on DVB core and I2C.

## Risks
There is no compile-time validation that the frontend pointer is non-NULL. A negative or too-large slew value intentionally disables slew in the implementation; board code must choose sane values if voltage ramping is required.

## Test Signals
Review parent-board data for correct frontend ownership and address selection. Runtime validation is through successful A8293 probe and working `set_voltage` calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/a8293.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/af9013.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/af9013.c

## Purpose
`af9013.c` implements the Afatech AF9013 DVB-T demodulator as an I2C client driver. It exposes a DVB frontend, firmware download path, I2C mux for tuner access, regmap-backed register access, status/statistics reporting, and PID filter callbacks.

## Important APIs, Types, And Functions
`struct af9013_state` owns the I2C client, custom regmap, `i2c_mux_core`, DVB frontend, platform configuration, GPIO values, cached bandwidth/status/statistics, and jiffy timestamps for polling throttles. Important functions include `af9013_probe()`, `af9013_init()`, `af9013_sleep()`, `af9013_set_frontend()`, `af9013_get_frontend()`, `af9013_read_status()`, `af9013_download_firmware()`, `af9013_pid_filter_ctrl()`, `af9013_pid_filter()`, `af9013_select()`, `af9013_deselect()`, and custom `af9013_regmap_read/write()` hooks.

## Control Flow
Probe copies `af9013_platform_data`, initializes regmap with 24-bit virtual register addresses, creates one I2C mux adapter, optionally downloads `dvb-fe-af9013.fw`, reads firmware version, configures GPIOs, copies `af9013_ops`, and returns callbacks through platform data. Init powers ADC/reset paths, writes firmware API version, configures ADC clock, loads demod core table and tuner-specific table from `af9013_priv.h`, sets TS output mode, enables lock LED, and marks the first tune. Tuning first calls attached tuner `set_params`, writes bandwidth CFOE coefficients, computes IF frequency control and spectrum inversion, clears lock flags, programs DVB-T transmission parameters, chooses auto/manual easy mode, and resets the FSM.

## State And Persistence
Persistent runtime state is in `af9013_state`: last bandwidth, first-tune flag, cached DVBv3 metrics, cumulative uncorrected blocks, and jiffy-based read throttles. Firmware is loaded into hardware RAM but not persisted by the driver. The I2C mux gate state is controlled by register bits and not reference-counted outside the mux framework.

## Dependencies And Integration Points
The driver depends on DVB core, I2C, I2C mux, regmap, firmware loader, integer log math, and tuner callbacks. Parent drivers consume `get_dvb_frontend`, `get_i2c_adapter`, and PID filter callbacks from platform data. Register tables and supported tuner IDs come from `af9013_priv.h`/`af9013.h`.

## Risks
Probe assumes complete platform data. Firmware absence fails non-USB mode probe. Custom regmap virtual lock bits and direct `__i2c_transfer()` make bus-lock behavior subtle. Signal strength math divides by tuner AGC calibration differences and assumes valid table data. Status and statistics are cached for 2 seconds, so tests may see delayed changes. PID filter silently accepts virtual PID values above `0x1fff`.

## Test Signals
Probe should log firmware version and successful attach. Integration tests need cold/warm firmware paths, muxed tuner I2C access, DVB-T tune across 6/7/8 MHz bandwidths, statistics polling, suspend/sleep, and PID filter programming. Fault injection should target firmware request, regmap read/write, mux add/remove, and invalid clock/bandwidth combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/af9013.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/af9013.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/af9013.h

## Purpose
This public header describes board/platform configuration for the Afatech AF9013 DVB-T demodulator and declares tuner, TS mode, GPIO, and callback contracts.

## Important APIs And Types
`struct af9013_platform_data` includes `clk`, `tuner`, `if_frequency`, `ts_mode`, `ts_output_pin`, `spec_inv`, `api_version[4]`, and `gpio[4]`. It also contains callbacks populated by the driver: `get_dvb_frontend`, `get_i2c_adapter`, `pid_filter_ctrl`, and `pid_filter`. The header defines tuner IDs for MaxLinear, Panasonic, Microtune, Freescale, Quantek, and NXP tuners, TS modes `USB`, `PARALLEL`, and `SERIAL`, and GPIO bit flags such as `AF9013_GPIO_ON`, `AF9013_GPIO_EN`, `AF9013_GPIO_O`, and derived tuner on/off macros.

## Control Flow And Integration
Parent USB/PCI/board drivers provide this platform data when registering the I2C client. After probe, they use the returned callback pointers to obtain the DVB frontend, access a gated tuner I2C adapter, and program the demod PID filter.

## State And Persistence
The struct is probe-time configuration plus callback handoff. Runtime state is copied into `af9013_state`; callback pointers are written back into the platform-data object.

## Dependencies
The header includes `<linux/dvb/frontend.h>` and references `struct i2c_client`, `struct i2c_adapter`, and `struct dvb_frontend` through kernel declarations. Kconfig requires DVB core, I2C, I2C mux, and regmap.

## Risks
Tuner IDs and clock values must match the private initialization tables and coefficient tables. Incorrect IF frequency or spectrum inversion gives lock failures that look like RF issues. GPIO meanings are partly guessed in comments, so board-specific mistakes are plausible.

## Test Signals
Validate platform data against known device IDs and tuner models. Confirm the driver writes back non-NULL callbacks and that the returned I2C adapter reaches the tuner.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/af9013.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/af9013_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/af9013_priv.h

## Purpose
This private header supplies AF9013 implementation data: firmware name, helper structs, bandwidth coefficients, demodulator initialization registers, and tuner-specific initialization tables.

## Important APIs And Types
`AF9013_FIRMWARE` is `"dvb-fe-af9013.fw"`. `struct af9013_reg_mask_val` represents masked register updates, and `struct af9013_coeff` maps clock/bandwidth pairs to 24-byte CFOE coefficient values. `coeff_lut` covers 28.8, 20.48, 28, and 25 MHz clocks for 6/7/8 MHz bandwidths. `demod_init_tab` is the core demod table. Tuner tables include `tuner_init_tab_env77h11d5`, `mt2060`, `mt2060_2`, `mxl5003d`, `mxl5005`, `qt1010`, `mc44s803`, `unknown`, and `tda18271`.

## Control Flow And Integration
`af9013.c` includes this header directly. During `af9013_init()`, it writes `demod_init_tab` first, then selects one tuner table based on `state->tuner`. During `af9013_set_frontend()`, it selects a `coeff_lut` entry based on `state->clk` and requested bandwidth. Metrics code also depends on `<linux/int_log.h>` included here for CNR calculations.

## State And Persistence
The file is static read-only data compiled into the module. It does not allocate runtime state. Hardware state changes happen when the tables are replayed into registers.

## Dependencies
The header is private to the AF9013 driver and depends on DVB frontend definitions, firmware loader, I2C mux, math64, regmap, and public AF9013 platform definitions.

## Risks
Unsupported clock/bandwidth combinations fail tuning. The register tables are opaque vendor/device data; table corruption can break tuning, AGC, metrics, or TS output without compiler warnings. Some tuner tables enable signal-strength calibration registers; missing calibration makes strength unavailable or inaccurate.

## Test Signals
Table coverage should be tested through targeted init for each supported tuner ID and tune across 6/7/8 MHz for each supported clock. Static review should ensure table names remain aligned with public tuner constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/af9013_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/af9033.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/af9033.c

## Purpose
`af9033.c` implements the Afatech AF9033/AF9035 and IT9135 DVB-T demodulator family as an I2C client driver. It exposes a DVB frontend, optional PID filter callbacks, I2C gate control, and regmap-backed configuration/status handling.

## Important APIs, Types, And Functions
`struct af9033_dev` stores the client, regmap, frontend, copied `af9033_config`, chip-family flags, TS mode booleans, bandwidth cache, FE status, and cumulative BER/block counters. Key functions include `af9033_probe()`, `af9033_init()`, `af9033_sleep()`, `af9033_set_frontend()`, `af9033_get_frontend()`, `af9033_read_status()`, DVBv3 metric adapters, `af9033_i2c_gate_ctrl()`, `af9033_pid_filter_ctrl()`, and `af9033_pid_filter()`. `af9033_wr_reg_val_tab()` optimizes contiguous private register tables into bulk writes.

## Control Flow
Probe copies platform config, records TS mode, currently rejects clocks other than 12 MHz, initializes a 24-bit regmap over I2C, detects IT9135 versus AF9035 by tuner ID, reads firmware versions, optionally sleeps AF9035 hardware, installs frontend ops, returns frontend/regmap through config, and populates PID filter ops. Init writes main and ADC clock controls from lookup tables, applies core config masks, handles TS mode and dynamic clock settings, selects OFSM init table by chip/tuner family, selects tuner-specific init table, and initializes DVBv5 stats. Tuning validates 6/7/8 MHz bandwidth, calls tuner `set_params`, writes bandwidth coefficients, computes IF frequency control from ADC clock and tuner IF, programs bandwidth/VHF-UHF mode, and resets the FSM.

## State And Persistence
Runtime state includes current bandwidth, family flags, cumulative post-bit/block counters, and `fe_status`. Counters accumulate while locked and are exposed through DVBv5 statistics; `read_ber` returns delta since the previous old-API call. State is reset on driver removal, not persisted.

## Dependencies And Integration Points
The driver depends on DVB core, I2C, regmap I2C, int-log math, and tuner callbacks. Public config supplies `fe`, `ops`, and `regmap` out-pointers used by parent USB/bridge/tuner code. Private tables in `af9033_priv.h` control most device-specific initialization.

## Risks
The public header documents many clocks, but probe only accepts 12 MHz in this source, so platform configs using other advertised clocks fail. Tuner support is table-driven; unsupported tuner IDs fail init. Several tuner callback return values are ignored. Statistics depend on lock state and register interpretation differences between AF9035 and IT9135. Serial TS sleep path temporarily switches to parallel mode to avoid leakage, which can surprise code assuming TS config is unchanged during suspend.

## Test Signals
Probe logs firmware versions and attach success. Tests should cover AF9035 and IT9135 tuner IDs, TS USB/parallel/serial modes, 6/7/8 MHz tuning, I2C gate toggling, PID filter writes, and cumulative stats behavior. Negative tests should cover unsupported clock and tuner IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/af9033.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/af9033.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/af9033.h

## Purpose
This public header defines configuration and callback contracts for the AF9033 DVB-T demodulator family.

## Important APIs And Types
`struct af9033_config` contains clock, ADC multiplier, tuner ID, TS mode, spectrum inversion, dynamic clock flag, optional PID ops, frontend out-pointer, and regmap out-pointer for IT913x integrated tuner use. Tuner constants cover TUA9001, FC0011/FC0012/FC2580, MXL5007T, TDA18218, and IT9135/Omega variants. `struct af9033_ops` exposes `pid_filter_ctrl` and `pid_filter`.

## Control Flow And Integration
Parent drivers allocate/populate `af9033_config`, pass it as I2C platform data, and receive `*fe`, `ops`, and `regmap` during probe. The demodulator uses tuner ID to select private init data and family behavior. TS mode determines output register programming and sleep handling.

## State And Persistence
The config is copied into internal driver state at probe. The out-pointers become integration handles for parent code but do not persist beyond device lifetime.

## Dependencies
The header references DVB frontend and regmap types. Kconfig selects `REGMAP_I2C` and depends on DVB core and I2C.

## Risks
The clock comment lists many possible clock values, but this implementation currently rejects anything except `12000000`. The `fe` pointer must point to storage for a `struct dvb_frontend *`; a bad pointer will corrupt parent memory. Tuner IDs must match private tables.

## Test Signals
Validate parent config with known device descriptors. Confirm probe populates frontend, regmap, and PID ops for supported tuner IDs, and verify unsupported clocks fail predictably.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/af9033.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/af9033_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/af9033_priv.h

## Purpose
This private header is the AF9033/AF9035/IT9135 device-data repository. It provides register table structs, clock/ADC lookup data, bandwidth coefficients, OFSM init tables, tuner init tables, and power-reference data for signal strength.

## Important APIs And Types
`struct reg_val`, `struct reg_val_mask`, `struct coeff`, `struct clock_adc`, and `struct val_snr` model register writes and lookup data. `clock_adc_lut` maps crystal clocks to ADC clocks. `coeff_lut` stores 36-byte coefficient sets. Init tables include `ofsm_init`, `ofsm_init_it9135_v1`, and `ofsm_init_it9135_v2`. Tuner tables include TUA9001, FC0011, FC0012, MXL5007T, TDA18218, FC2580, and IT9135 variants 38/51/52/60/61/62. `power_reference` gives NorDig reference levels indexed by modulation and code rate.

## Control Flow And Integration
`af9033.c` selects an OFSM table by tuner family, then selects a tuner init table by exact tuner ID. Tuning uses `clock_adc_lut` and `coeff_lut`. Signal-strength logic for IT9135 uses `power_reference` together with TPS registers.

## State And Persistence
All content is static const module data. Hardware register state is created by replaying these tables during init and tuning.

## Dependencies
The file depends on DVB frontend definitions, the public AF9033 header, math64, regmap, kernel helpers, and integer log support.

## Risks
Most hardware behavior is encoded as opaque register constants. Table mistakes can cause silent lock failures, wrong TS output, poor sensitivity, or bad metrics. The coefficient table in this tree contains entries only for 12 MHz in the visible data used by current probe constraints, so adding clocks requires synchronized table and probe work.

## Test Signals
Exercise every supported tuner ID through init. Validate coefficient selection for every accepted bandwidth and clock. Compare strength/CNR values against known-good hardware measurements where possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/af9033_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/as102_fe.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/as102_fe.c

## Purpose
`as102_fe.c` implements a DVB-T frontend shim for Abilis AS102 receivers. It translates Linux DVB frontend operations to device-specific callback operations supplied by the parent AS102 transport driver.

## Important APIs, Types, And Functions
`struct as102_state` contains the DVB frontend, cached demod stats, callback table, private parent pointer, eLNA config, signal strength, and BER. `as102_attach()` allocates state, installs `as102_fe_ops`, stores callbacks, and returns a frontend. Important operations are `as102_fe_set_frontend()`, `as102_fe_get_frontend()`, `as102_fe_read_status()`, DVBv3 metric readers, `as102_fe_ts_bus_ctrl()`, and `as102_fe_release()`.

## Control Flow
Set-frontend converts DVB property cache values into packed AS10x tuning arguments: frequency in kHz, bandwidth, guard interval, modulation, transmission mode, hierarchy, and code rate selection. It then calls parent `set_tune`. Get-frontend calls `get_tps` and maps hardware TPS fields back into DVB properties. Read-status calls `get_status`, updates cached signal/BER, maps tune state into FE status flags, clears demod stats if not locked, and calls `get_stats` when locked. TS bus control calls parent `stream_ctrl` with acquire flag and eLNA config.

## State And Persistence
The driver caches demod stats, signal strength, and BER inside `as102_state`. There is no persistent storage. Cached stats are cleared on unlock and freed on release.

## Dependencies And Integration Points
The file depends on DVB frontend core and AS10x command structure definitions from `as102_fe_types.h`. It does not know the USB/control transport; all hardware access is through `struct as102_fe_ops` callbacks.

## Risks
Callback pointers are assumed valid. Unsupported or AUTO values often map to device `UNKNOWN` constants rather than hard errors, so bad tuning input may fail only by not locking. `as102_fe_read_signal_strength()` uses a questionable arithmetic scaling expression that can overflow or produce nonstandard values depending on `signal_strength`. Only PAL/NTSC concerns are irrelevant here; this is DVB-T only.

## Test Signals
Mock callback tests can verify DVB-to-AS10x mapping. Hardware tests should tune 6/7/8 MHz channels, test hierarchy/code-rate selection, lock/unlock status transitions, stats refresh, and TS bus acquire/release behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/as102_fe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/as102_fe.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/as102_fe.h

## Purpose
This header defines the callback interface and attach function for the AS102 DVB-T frontend shim.

## Important APIs And Types
`struct as102_fe_ops` provides parent-supplied callbacks: `set_tune`, `get_tps`, `get_status`, `get_stats`, and `stream_ctrl`. `as102_attach()` takes a frontend name, ops table, private parent pointer, and eLNA config, returning a `struct dvb_frontend *`.

## Control Flow And Integration
The AS102 transport/USB driver calls `as102_attach()` and implements the callback table using its command protocol. The frontend file translates standard DVB operations into these callbacks.

## State And Persistence
This header declares only contracts. Runtime state is allocated in `as102_fe.c` and stores the callback pointers and private context.

## Dependencies
The header includes AS10x packed command/status types from `as102_fe_types.h` and relies on DVB frontend declarations being available through implementation includes.

## Risks
The callback table is not optional in the implementation; missing functions will crash when frontend ops are invoked. ABI-like packed structs must stay synchronized with firmware/control-protocol expectations.

## Test Signals
Compile checks should catch callback signature mismatches. Runtime tests should confirm all callbacks are called with the expected private pointer and arguments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/as102_fe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/as102_fe_types.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/as102_fe_types.h

## Purpose
This header defines AS10x firmware/control-protocol constants and packed structures used by the AS102 frontend shim and parent transport code.

## Important APIs And Types
Constants encode bandwidths, hierarchy priority, modulation, hierarchy alpha, interleaving, FEC code rates, guard intervals, transmission modes, DVB-H flags, tune states, TS PID filter types, context IDs, and configuration modes. Packed structs include `as10x_tps`, `as10x_tune_args`, `as10x_tune_status`, `as10x_demod_stats`, `as10x_ts_filter`, `as10x_register_value`, and `as10x_register_addr`.

## Control Flow And Integration
`as102_fe.c` fills `as10x_tune_args` from DVB frontend properties, reads `as10x_tps` and `as10x_tune_status` through callbacks, and caches `as10x_demod_stats` for metric readers. Parent transport code serializes these packed structs to the hardware.

## State And Persistence
No runtime state exists in the header. The packed structs represent transient command and response payloads.

## Dependencies
The file relies on fixed-width integer types and `__packed` kernel annotation. Correct packing is essential for firmware protocol compatibility.

## Risks
Changing numeric constants or packing breaks device protocol. Several values use `0xff` as unknown/error sentinel, so conversion code must preserve those semantics. Endianness is implicit in field serialization by parent code and should be reviewed if moving across transports.

## Test Signals
Protocol tests should verify `sizeof()` and field offsets for each packed struct. Mock command tests should validate DVB property conversion against expected byte payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/as102_fe_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ascot2e.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ascot2e.c

## Purpose
`ascot2e.c` implements a Sony ASCOT2E terrestrial/cable tuner driver that attaches tuner operations to an existing DVB frontend.

## Important APIs, Types, And Functions
`struct ascot2e_priv` stores current frequency, 7-bit I2C address, adapter, power state, and optional active-tuner callback. Internal enums describe power state and TV system variants for DVB-T, DVB-T2, DVB-C Annex A, and DVB-C2-like table entries. Core functions are I2C helpers, power-save transitions, `ascot2e_get_tv_system()`, `ascot2e_set_params()`, `ascot2e_get_frequency()`, and exported `ascot2e_attach()`.

## Control Flow
Attach allocates private state, opens the demod I2C gate if available, writes boot/PLL/RSSI/default power-save registers, closes the gate, installs `dvb_tuner_ops`, and stores `fe->tuner_priv`. Set-params maps delivery system and bandwidth to a table entry, optionally notifies parent tuner selection, leaves power save, rounds frequency to 25 kHz, programs IF/AGC/filter/LNA settings, writes frequency and bandwidth registers, waits for VCO calibration, returns CPU/logic to sleep, records frequency, and returns.

## State And Persistence
The driver tracks only current tuned frequency and sleep/active state in memory. Hardware registers hold the actual tuner configuration until power loss or reprogramming.

## Dependencies And Integration Points
It depends on DVB frontend core, Linux I2C, and the demod frontend's optional `i2c_gate_ctrl`. `ascot2e_attach()` is exported and guarded by a Kconfig stub in the header.

## Risks
`config->xtal_freq_mhz` is documented but attach writes a fixed 16 MHz value, so non-16 MHz boards may not work. Many I2C writes ignore return values in attach and tune sequences, which can hide partial programming. Unsupported delivery systems return `-EINVAL`. The I2C address is shifted right by one, assuming callers pass an 8-bit address.

## Test Signals
Hardware tune tests should cover DVB-T/T2/C bandwidths and sleep/resume transitions. Fault injection should validate I2C failure propagation in helpers and expose ignored errors. Confirm parent active-tuner callback sequencing when multiple tuners share resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ascot2e.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ascot2e.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ascot2e.h

## Purpose
This public header declares configuration and attach API for the Sony ASCOT2E tuner driver.

## Important APIs And Types
`struct ascot2e_config` includes `i2c_address`, `xtal_freq_mhz`, optional callback private data, and `set_tuner_callback`. `ascot2e_attach()` attaches tuner ops to a supplied DVB frontend when `CONFIG_DVB_ASCOT2E` is reachable; otherwise an inline stub logs that the driver is disabled and returns NULL.

## Control Flow And Integration
Demod/bridge drivers call `ascot2e_attach(fe, config, i2c)` after creating the demod frontend. The tuner driver then populates `fe->ops.tuner_ops` and uses optional demod `i2c_gate_ctrl` during attach.

## State And Persistence
The header holds configuration only. Private runtime state is allocated by `ascot2e.c`.

## Dependencies
It includes DVB frontend and I2C headers. Kconfig requires DVB core and I2C.

## Risks
The implementation currently uses a fixed 16 MHz setup despite the `xtal_freq_mhz` field, so the public contract and implementation may diverge. Callers must understand whether `i2c_address` is 8-bit or 7-bit formatted because implementation shifts it.

## Test Signals
Compile both enabled and disabled Kconfig cases. Runtime attach should return the original frontend on success, set tuner ops, and log the attached address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ascot2e.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/atbm8830.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/atbm8830.c

## Purpose
`atbm8830.c` implements the AltoBeam ATBM8830/8831 GB20600/DMB-TH demodulator as an attach-style DVB frontend driver.

## Important APIs, Types, And Functions
The driver uses `struct atbm_state` from the private header. Core helpers are `atbm8830_write_reg()`, `atbm8830_read_reg()`, `set_osc_freq()`, `set_if_freq()`, `set_agc_config()`, `set_static_channel_mode()`, `set_ts_config()`, `atbm8830_init()`, `atbm8830_set_fe()`, metric readers, `atbm8830_i2c_gate_ctrl()`, and exported `atbm8830_attach()`.

## Control Flow
Attach validates config/I2C, allocates state, reads chip ID, copies frontend ops, initializes the device immediately, opens the I2C gate, and returns the frontend. Init writes oscillator and IF frequency words, AGC limits, static-channel tuning registers, TS mode registers, releases reset, writes a software-version-test register, and starts demod run. Tuning delegates RF programming to `fe->ops.tuner_ops.set_params()` with I2C gate open, then polls lock up to ten times at 100 ms.

## State And Persistence
Runtime state is `atbm_state` with config pointer, I2C adapter, and frontend. No persistent storage exists. Hardware latches are used to make multi-register metric reads consistent.

## Dependencies And Integration Points
It depends on DVB frontend core, I2C, math/div64 helpers, and a board-supplied tuner attached to the frontend. `atbm8830_config` provides TS, clock, IF, zero-IF, and AGC parameters. The I2C gate lets downstream tuners share the bus through the demod.

## Risks
Many helper writes ignore return values, so init can report success after partial programming. `set_if_freq()` computes `(freq - fs)` with unsigned values, which is risky if IF is below oscillator frequency. SNR and uncorrected block reads are placeholders returning zero; get-frontend returns fixed/TODO values. Attach initializes hardware before a tuner may be fully configured by higher layers.

## Test Signals
Hardware tests should cover attach, chip ID read, init register writes, tuner bus gate, lock polling, BER and strength readings. Static tests should flag ignored I2C errors and unsigned arithmetic edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/atbm8830.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/atbm8830.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/atbm8830.h

## Purpose
This public header defines board configuration and attach API for the AltoBeam ATBM8830/8831 demodulator.

## Important APIs And Types
`struct atbm8830_config` carries product type, demod I2C address, TS serial/clock/sample settings, oscillator and IF frequencies in kHz, zero-IF IQ swap, and tuner AGC settings. Product constants are `ATBM8830_PROD_8830` and `ATBM8830_PROD_8831`. `atbm8830_attach()` is exported when reachable, otherwise an inline disabled-driver stub logs and returns NULL.

## Control Flow And Integration
Board drivers call `atbm8830_attach(config, i2c)`, then attach a tuner through the demod I2C gate as needed. The config values are used during immediate demod initialization.

## State And Persistence
The config is referenced by pointer in private state; callers must keep it valid for the frontend lifetime. No runtime state is declared in this header.

## Dependencies
The header includes DVB frontend and I2C declarations. Kconfig requires DVB core and I2C.

## Risks
Because the implementation stores the config pointer rather than copying it, stack-allocated configs would be unsafe. Units are kHz, not Hz, unlike many DVB properties. Incorrect TS clock or zero-IF settings can produce no transport stream despite RF lock.

## Test Signals
Validate config lifetime and units in parent drivers. Runtime attach should succeed only at the configured I2C address and tune with the configured TS/IF mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/atbm8830.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/atbm8830_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/atbm8830_priv.h

## Purpose
This private header defines ATBM8830 runtime state and symbolic register addresses used by `atbm8830.c`.

## Important APIs And Types
`struct atbm_state` stores the I2C adapter, const config pointer, and embedded DVB frontend. Register macros cover chip ID, baseband/IF/oscillator configuration, demod run/reset, TS output controls, lock status, ADC configuration, carrier offset, IF/OSC frequency words, analog-detection flags, frame error counters, IQ swap, TPS, AGC target/min/max/lock/PWM, and I2C gate control.

## Control Flow And Integration
`atbm8830.c` uses these macros in init, tuning, metrics, and I2C gate functions. Multi-byte values are written as adjacent little-endian registers. `REG_READ_LATCH` supports atomic multi-register metric reads.

## State And Persistence
The struct is heap-allocated during attach. Register macros are compile-time constants only.

## Dependencies
The header is private and assumes `struct atbm8830_config`, `struct i2c_adapter`, and `struct dvb_frontend` are visible through included implementation headers.

## Risks
Incorrect register constants directly affect hardware programming. Comments mark some adjacent ranges but no helpers enforce valid multi-byte access. The config pointer lifetime risk is defined here because the state stores `const struct atbm8830_config *`.

## Test Signals
Register-write tracing should confirm adjacent multi-byte writes match expected endianness. Static analysis should verify every macro use has error handling where feasible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/atbm8830_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/au8522.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/au8522.h

## Purpose
This public header defines configuration, attach API, and analog routing enums for the Auvitek AU8522 ATSC/QAM/NTSC demodulator family.

## Important APIs And Types
`enum au8522_if_freq` describes IF choices for VSB/QAM. `struct au8522_led_config` supplies LED threshold/GPIO programming and state masks. `struct au8522_config` contains demod I2C address, status mode (`AU8522_TUNERLOCKING` or `AU8522_DEMODLOCKING`), LED config pointer, and VSB/QAM IF selections. `au8522_attach()` is available when DTV support is reachable. Analog enums define composite/S-video video inputs and audio inputs `AU8522_AUDIO_NONE`/`AU8522_AUDIO_SIF`.

## Control Flow And Integration
DTV parent drivers call `au8522_attach()` from the unlisted digital implementation. V4L2 analog routing code in `au8522_decoder.c` uses the video/audio input enums. Common state and register helpers live in `au8522_common.c`.

## State And Persistence
This file declares configuration only. The common private state stores a copy of config and current analog/digital mode.

## Dependencies
It includes DVB frontend declarations. Analog users also rely on V4L2 subdev infrastructure through implementation files. Kconfig splits DTV and V4L modules while selecting common support.

## Risks
LED config pointers must remain valid if copied shallowly by implementation. Status mode changes lock interpretation. Unsupported analog input enum values return `-EINVAL` in the decoder.

## Test Signals
Build enabled/disabled attach stub cases. Runtime tests should verify IF selection, lock status mode, LED GPIO behavior, and V4L2 routing enum handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/au8522.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/au8522_common.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/au8522_common.c

## Purpose
`au8522_common.c` provides shared register access, state sharing, I2C gate control, LED control, and basic digital init/sleep helpers for AU8522 digital and analog modules.

## Important APIs, Types, And Functions
Exported functions include `au8522_writereg()`, `au8522_readreg()`, `au8522_i2c_gate_ctrl()`, `au8522_analog_i2c_gate_ctrl()`, `au8522_get_state()`, `au8522_release_state()`, `au8522_led_ctrl()`, `au8522_init()`, and `au8522_sleep()`. The file uses a global `hybrid_tuner_instance_list` and `au8522_list_mutex` with media hybrid-tuner helpers to share one `struct au8522_state` between DTV and V4L clients.

## Control Flow
Register writes send 16-bit register addresses with a write marker and one byte of data; reads send a read marker and receive one byte. Digital I2C gate control is suppressed when analog mode owns the chip, while analog gate control always writes the gate register. State acquisition/release is serialized through the global mutex. LED control enables GPIO output, clears previous LED bits, sets selected state, records `state->led_state`, and disables GPIO output when off. Digital init marks digital mode, clears cached frequency/modulation, powers/reset-writes register `0xa4`, and opens the gate. Sleep ignores requests if analog mode is active, otherwise turns off LED, powers down, and clears current frequency.

## State And Persistence
Shared runtime state lives in `au8522_state` from `au8522_priv.h` and is reference-managed through hybrid-tuner helpers. Important fields touched here include operational mode, current frequency, current modulation, LED state, config, and I2C adapter. No persistent storage exists.

## Dependencies And Integration Points
The file depends on Linux I2C, DVB frontend core, AU8522 private state, and exported-symbol linkage for `au8522_dig.c` and `au8522_decoder.c`. It mediates analog/digital coexistence on the same chip.

## Risks
Register helpers return `-1` instead of standard negative errno in some failures. Read failures still return the received byte buffer value. Operational-mode checks are race-sensitive because DVB and V4L paths can switch modes while frontend threads are shutting down. Shallow LED config pointers require parent lifetime care.

## Test Signals
Exercise simultaneous analog/digital open/close paths, state reuse counts, gate writes in both modes, LED transitions, and error handling under I2C transfer failure. Logs from `debug` parameter help confirm common helper sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/au8522_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/au8522_decoder.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/au8522_decoder.c

## Purpose
`au8522_decoder.c` implements the AU8522 analog video decoder V4L2 subdevice side. It supports CVBS and S-video routing, limited NTSC/PAL-M standard setup, audio SIF setup, V4L2 controls, tuner signal reporting, and I2C-driver registration.

## Important APIs, Types, And Functions
The file defines filter coefficient tables, LP audio filter coefficients, V4L2 subdev ops, and I2C probe/remove. Important functions include `setup_decoder_defaults()`, `au8522_setup_cvbs_mode()`, `au8522_setup_cvbs_tuner_mode()`, `au8522_setup_svideo_mode()`, `set_audio_input()`, `au8522_s_ctrl()`, `au8522_video_set()`, `au8522_s_stream()`, `au8522_s_video_routing()`, `au8522_s_std()`, `au8522_s_audio_routing()`, `au8522_g_tuner()`, and `au8522_probe()`.

## Control Flow
Probe verifies I2C SMBus byte-data support, obtains shared AU8522 state, initializes the V4L2 I2C subdev, optionally sets media-controller pads, registers brightness/contrast/saturation/hue controls, initializes default NTSC/composite/no-audio state, and opens the tuner I2C gate. Starting stream clears digital current frequency, resets module control, programs video route defaults based on `state->vid_input`, configures audio, and marks analog mode. Stopping stream reduces power and marks suspend mode. Routing/std/audio setters update state and reprogram hardware if analog streaming is active. Tuner status reads decoder lock and PLL registers to report signal.

## State And Persistence
Analog state shares `struct au8522_state` with digital code. Fields include V4L2 subdev, control handler, media pads, standard, video input, audio input, operational mode, client pointer, id/rev, and digital caches cleared when analog starts. There is no persistence beyond module lifetime.

## Dependencies And Integration Points
The decoder depends on V4L2 core/subdev/control APIs, Linux I2C, AU8522 public/private headers, and common register/state helpers. It is built under `DVB_AU8522_V4L` and selects common support through Kconfig.

## Risks
Developer notes state that true analog demodulator code is not implemented; the driver is enough for CVBS/S-video inputs such as tuner-provided CVBS. Many register writes are fire-and-forget with no error propagation. Only a subset of routes is accepted despite enum definitions. Media-entity init failure returns without releasing shared state in that branch. The S-video path intentionally uses CVBS filter type due to hardware/board behavior, which is surprising but documented in comments.

## Test Signals
V4L2 tests should cover probe/remove, control writes, stream on/off, composite and S-video routing, PAL-M/NTSC standard changes, audio SIF enable/disable, ADV_DEBUG register access when enabled, and media-controller pad registration. Hardware tests should confirm analog/digital handoff does not corrupt the DTV frontend state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/au8522_decoder.c -->
