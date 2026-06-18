# subset-b-004194 research

Grouped research report for the requested media tuner files. Each section is keyed by original source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/si2157.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/si2157.c

Purpose: implements the Silicon Labs Si2141/2146/2147/2148/2157/2158/2177 tuner as a modern I2C client driver that installs `dvb_tuner_ops` onto a supplied frontend. It handles firmware command transport, firmware upload and revision detection, digital and analog tuning, RSSI reporting, sleep, remove, and optional media-controller entity registration.

Important APIs and functions: module entry is `module_i2c_driver(si2157_driver)` with `si2157_probe` and `si2157_remove`. The frontend operations are `si2157_init`, `si2157_sleep`, `si2157_set_params`, `si2157_set_analog_params`, `si2157_get_frequency`, `si2157_get_bandwidth`, `si2157_get_if_frequency`, and `si2157_get_rf_strength`. `si2157_cmd_execute` is the central serialized firmware-command helper; `si2157_find_and_load_firmware` chooses firmware from part/ROM IDs and `si2157_load_firmware` streams 17-byte firmware records.

Control flow: probe allocates `struct si2157_dev`, copies platform config, checks that the device answers a status read, installs tuner ops, and optionally registers media pads. `init` first tries a warm-state property read, otherwise powers up with part-specific command bytes, loads firmware unless disabled, reboots firmware, queries the version, enables tuner status flags, initializes signal-stat metadata, and starts delayed RSSI polling. Digital tuning maps delivery system and bandwidth to SiLabs command fields, programs IF port and IF frequency, tunes RF frequency, updates cached state, and waits for tune completion. Analog tuning validates part support, derives TV standard, center frequency, bandwidth, IF and inversion settings, programs analog properties, and performs special Si2177 retune/restart sequences. Sleep cancels stats polling and sends standby.

State and persistence: all persistent software state is in `struct si2157_dev`: `active`, part ID, IF port, inversion, firmware-skip flag, cached frequency/bandwidth/IF, an I2C mutex, delayed work, and optional media entity/pads. Hardware and firmware state persists in the tuner until power/standby; the driver invalidates cached IF/frequency state on failed tuning and warm-state uncertainty.

Dependencies and integration points: depends on Linux I2C, firmware loader, delayed work, DVB frontend properties, V4L2 analog parameters, and optional media-controller APIs. It integrates through `client->dev.platform_data` carrying `struct si2157_config`, `fe->tuner_priv = client`, and `fe->ops.tuner_ops`. Firmware names are advertised with `MODULE_FIRMWARE`.

Risks: most register command payloads are opaque byte sequences, so regressions are hard to review without hardware documentation. Some tune waits are intentionally ignored after programming, leaving possible silent lock failures. Analog support is limited to selected parts and FM radio explicitly returns `-EINVAL`. The Si2177 analog path includes debug/error logging and repeated property programming that looks less mature than digital tuning. Delayed stats work performs I2C reads periodically and must be cancelled on sleep/remove.

Test signals: compile with `CONFIG_MEDIA_TUNER_SI2157`, I2C probe/remove on all supported part IDs, firmware-present and firmware-missing paths, warm init after suspend/resume, digital tuning for ATSC/DVB-T/T2/DVB-C/ISDB-T/DTMB bandwidths, analog TV standards on supported parts, RSSI scale updates, and media-controller entity registration when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/si2157.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/si2157.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/si2157.h

Purpose: public configuration header for the Si2157-family I2C client driver.

Important APIs and types: defines `struct si2157_config` with the frontend pointer, optional `struct media_device *mdev`, spectral inversion bit, firmware-load suppression bit, and IF port selection. The note documents the common I2C address as `0x60`.

Control flow: board or bridge drivers populate this structure as `client->dev.platform_data` before creating the I2C client. `si2157_probe` consumes it, installs tuner ops into `cfg->fe`, and optionally registers a media-controller tuner entity.

State and persistence: this header owns no runtime state. Its bitfields become initial values in `struct si2157_dev`; later state such as active tuning and firmware revision is private to the implementation.

Dependencies and integration points: includes DVB frontend and media-device definitions and is included by `si2157_priv.h`. It is the external contract between bridge drivers and the tuner module.

Risks: there is no explicit platform-data validation in the header; a missing `fe` pointer or invalid IF port would fail at runtime. The media-device field is conditional on `CONFIG_MEDIA_CONTROLLER`, so users must keep initializers configuration-aware.

Test signals: build bridge drivers with and without media-controller support, instantiate an I2C client with populated config, and verify the frontend receives Si2157 tuner ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/si2157.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/si2157_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/si2157_priv.h

Purpose: private definitions for the Si2157-family tuner driver.

Important APIs and types: defines media pad indices, `struct si2157_dev`, supported part IDs, `struct si2157_tuner_info`, command buffer `struct si2157_cmd`, capability macros `SUPPORTS_1700KHz` and `SUPPORTS_ATV_IF`, and all firmware filename constants.

Control flow: `si2157.c` uses this header to track driver state, choose firmware based on part/ROM ID, bound firmware command argument length, and branch analog/bandwidth behavior by chip capability. Media pad definitions are used only when media-controller support is compiled.

State and persistence: `struct si2157_dev` holds the mutex that serializes command transport, frontend pointer, active/inversion/firmware flags, part and IF port IDs, cached IF/bandwidth/frequency, delayed stats work, and optional media entity state.

Dependencies and integration points: includes firmware loading, V4L2 media-controller helpers, and the public `si2157.h`. It is private to the module and should not be used by board drivers.

Risks: firmware filename constants are part of userspace deployment expectations; renaming or incorrect fallback selection can break devices. `SI2158_50_FIRMWARE` points to a `si2178`-named file, which may be intentional legacy naming but is easy to misread. The command buffer has a hard 30-byte limit that all opaque command arrays must respect.

Test signals: compile-time coverage of all part-specific firmware declarations, firmware request tests for old and new names, and probe logs confirming detected part IDs map to expected capability branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/si2157_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda18212.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/tda18212.c

Purpose: implements the NXP TDA18212HN silicon tuner as a regmap-backed I2C client driver for digital TV frontends.

Important APIs and functions: `tda18212_probe` and `tda18212_remove` are bound by `module_i2c_driver`. Frontend tuner operations are `tda18212_set_params` and `tda18212_get_if_frequency`. `struct tda18212_dev` stores copied config, I2C client, regmap, and current IF.

Control flow: probe allocates state, copies platform config, initializes an 8-bit regmap, opens the frontend I2C gate if present, reads chip ID register `0x00`, accepts master `0xc7` or slave `0x47`, installs tuner ops, and stores client data. `set_params` opens the I2C gate, maps delivery system and exact bandwidth to a row of register parameters and configured IF kHz, writes delivery-system registers, bulk-writes IF/RF frequency bytes, caches the rounded IF frequency, and closes the gate on both success and failure.

State and persistence: the only cached runtime value is the actual IF frequency in Hz, rounded through the hardware register encoding. Hardware configuration is written on each tune and is not restored from a software register image.

Dependencies and integration points: depends on Linux regmap-I2C, DVB frontend properties, and `struct tda18212_config` from the header. Integration is via platform data and `fe->tuner_priv = dev`.

Risks: bandwidth handling for DVB-T/T2 requires exact 6/7/8 MHz values; unsupported values return `-EINVAL`. The config has an `if_dvbt2_5` member but this implementation does not support a 5 MHz DVB-T2 branch. Probe assumes valid platform data. Most register settings are static tables with little local explanation.

Test signals: module build, ID detection for master and slave parts, I2C-gated tune transactions, IF-frequency readback matching rounded register values, and negative tests for unsupported delivery systems or bandwidths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda18212.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda18212.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/tda18212.h

Purpose: public configuration contract for the TDA18212HN tuner I2C client.

Important APIs and types: defines `struct tda18212_config`, containing per-standard IF values in kHz for DVB-T, DVB-T2, DVB-C, ATSC VSB/QAM, plus the frontend pointer consumed by probe.

Control flow: bridge drivers provide this structure as I2C platform data; `tda18212_probe` copies it and later `tda18212_set_params` selects IF values from it according to `dtv_property_cache`.

State and persistence: no state is owned by the header. Config values are copied into the driver's private state and used as persistent tuning policy.

Dependencies and integration points: includes DVB frontend definitions. It is used by board code and `tda18212.c`; unlike older attach-style tuner headers, it declares no attach function because the driver is instantiated as an I2C client.

Risks: no default IF values are provided; callers must initialize all fields relevant to their supported delivery systems. The `if_dvbt2_5` field is present but unused by this implementation.

Test signals: compile bridge initializers, verify platform-data values drive IF programming, and check that missing or zero IF fields are caught in board-level tuning validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda18212.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda18218.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/tda18218.c

Purpose: implements the older attach-style NXP TDA18218HN tuner driver.

Important APIs and functions: exported entry point is `tda18218_attach`. Tuner ops are `tda18218_init`, `tda18218_sleep`, `tda18218_set_params`, `tda18218_get_if_frequency`, and `tda18218_release`. I2C helpers `tda18218_wr_regs`, `tda18218_rd_regs`, `tda18218_wr_reg`, and `tda18218_rd_reg` implement chunked register access.

Control flow: attach allocates private state, opens the I2C gate, reads ID register zero, checks it against the default image, installs tuner ops, copies default registers, optionally adjusts loop-through standby defaults, writes standby, and closes the gate. Init writes the complete default register image. `set_params` opens the gate, derives IF and low-pass cutoff from bandwidth, computes LO frequency, selects band-pass filter by LO range, writes IF and LO divider bytes, toggles `Freq_prog_Start`, then runs a fixed AGC trigger sequence.

State and persistence: `struct tda18218_priv` stores config pointer, I2C adapter, cached IF frequency, and a 59-byte register image. The register image is mostly default/static; `set_params` writes derived fields but does not update every byte in the cache after each transfer.

Dependencies and integration points: depends on DVB frontend attach conventions, Linux I2C messages, and optional frontend I2C gate callbacks. Board drivers call `tda18218_attach` directly.

Risks: transfer chunking depends on `cfg->i2c_wr_max`; invalid zero or one values could break loop progress. Read always starts from register zero and copies out the requested slice, which is hardware-specific. Calibration is marked TODO, so performance may depend on defaults. Error handling during attach can return without closing the I2C gate in the chip-ID failure path.

Test signals: attach/probe ID read, gated full-register init, tune for 6/7/8 MHz bandwidths, IF frequency reporting of 3/3.5/4 MHz, loop-through standby behavior, and I2C failure injection around chunked writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda18218.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda18218.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/tda18218.h

Purpose: public attach/configuration header for the TDA18218HN tuner.

Important APIs and types: defines `struct tda18218_config` with I2C address, maximum write size, and loop-through flag. Declares `tda18218_attach` when reachable and provides a disabled-driver inline stub otherwise.

Control flow: board drivers call `tda18218_attach(fe, i2c, cfg)`; on success the implementation installs tuner ops into `fe`.

State and persistence: no direct state. Config is referenced by the private state rather than copied, so the caller-provided config must remain valid while the tuner is attached.

Dependencies and integration points: includes DVB frontend definitions and relies on Kconfig symbol `CONFIG_MEDIA_TUNER_TDA18218` for attach availability.

Risks: `i2c_wr_max` is a behavioral limit used in arithmetic in the C file and should be validated by board code. The disabled-driver stub only logs and returns `NULL`, so callers must handle failed attachment.

Test signals: compile with built-in, module, and disabled tuner configs; attach success on known hardware; and board config review for valid write-size and I2C address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda18218.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda18218_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/tda18218_priv.h

Purpose: private register map and state definitions for the TDA18218HN driver.

Important APIs and types: defines register offsets `R00_ID` through `R3A_FMAX2`, `TDA18218_NUM_REGS`, and `struct tda18218_priv` containing config, adapter, IF cache, and register image.

Control flow: the C file uses symbolic offsets to build bulk writes for default init, IF/filter programming, LO divider programming, AGC sequences, and standby power bits.

State and persistence: the `regs` array acts as a baseline software image of default register values and selected loop-through modifications. Hardware state is programmed from this image during init and selectively changed during tuning.

Dependencies and integration points: includes only the public TDA18218 header. It is private to the implementation and not a board-driver API.

Risks: register comments are terse and some labels appear copy-pasted, so field-level meaning is not self-validating. Any mismatch between `TDA18218_NUM_REGS` and default image length would corrupt init coverage. Since the config pointer is stored directly, lifetime is external.

Test signals: build-time coverage of all offsets, attach/init writing exactly 59 registers, and hardware readback or trace comparison after loop-through and standby changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda18218_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda18250.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/tda18250.c

Purpose: implements the NXP TDA18250A/B silicon tuner as a regmap-backed I2C client driver for digital TV.

Important APIs and functions: `tda18250_probe` and `tda18250_remove` are the I2C-driver hooks. Tuner ops are `tda18250_init`, `tda18250_set_params`, `tda18250_get_if_frequency`, and `tda18250_sleep`. Internal helpers handle power mode (`tda18250_power_control`), IRQ polling (`tda18250_wait_for_irq`), AGC programming (`tda18250_set_agc`), and PLL divider/current calculation (`tda18250_pll_calc`).

Control flow: probe validates config, creates a regmap with volatile ranges, reads three ID bytes, distinguishes master/slave and A/B revisions, installs tuner ops, then puts hardware in standby. Init powers up, writes default register tables and crystal-specific registers on first cold init, configures loop-through, runs hardware init and calibration state machines with IRQ polling, marks warm, and powers the LNA. `set_params` chooses delivery-system table rows and IF values, writes masked register fields, updates IF if changed, programs AGC, writes RF frequency bytes, performs an initial tune, calculates PLL parameters from hardware MD state, adjusts crystal/charge-pump fields, tunes again, waits for lock, restores AGC control, and returns. Sleep powers down LNA, clears IF cache, and enters standby with loop-through-specific behavior.

State and persistence: `struct tda18250_dev` stores frontend, regmap, crystal selector, configured IFs, current IF in kHz, slave/loop-through/warm flags, and an unused register array. Regmap caches nonvolatile registers while declared volatile ranges are read from hardware.

Dependencies and integration points: depends on regmap-I2C, DVB frontend properties, platform-data `struct tda18250_config`, and kernel timing/IRQ polling helpers. It uses `fe->tuner_priv = client`, so tuner ops recover state through I2C client data.

Risks: `regmap_bulk_read` in probe does not check its return before using `chip_id`. `tda18250_pll_calc` computes `1 << (exp - 1)` after forcing invalid `exp` to zero, which can become an invalid negative shift if hardware returns unexpected MD bits. Tuning is highly table-driven with opaque constants and many sequential register writes, so partial failures leave hardware in an intermediate state.

Test signals: probe IDs for A/B master/slave parts, valid/invalid crystal config, cold and warm init, standby with and without loop-through, IRQ timeout behavior for init/cal/tune, DVB-T/T2/DVB-C/ATSC tuning across bandwidths and RF ranges, and IF readback in Hz.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda18250.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda18250.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/tda18250.h

Purpose: public configuration header for the TDA18250 tuner I2C client.

Important APIs and types: defines crystal-frequency selector constants, `TDA18250_XTAL_FREQ_MAX`, and `struct tda18250_config` with IF values, crystal selector, loop-through flag, frontend pointer, and optional media-device pointer.

Control flow: bridge code supplies this as I2C platform data. Probe validates `xtal_freq`, copies IFs and loop-through into private state, and later init/tune use those values for crystal register tables and IF programming.

State and persistence: no runtime state in the header. The config fields become persistent private policy in `struct tda18250_dev`.

Dependencies and integration points: includes kconfig, DVB frontend, and media-device headers. It is consumed by `tda18250.c` and board drivers that create the I2C client.

Risks: no attach stub is provided because this is not attach-style; users must instantiate an I2C device. Invalid or uninitialized `xtal_freq` prevents probe. Optional media-controller field is present but this implementation does not register a media entity.

Test signals: platform-data initializer builds, crystal selector validation, IF value propagation to tuning, and configs compiled with and without media-controller support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda18250.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda18250_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/tda18250_priv.h

Purpose: private register map, IRQ constants, power constants, and state type for the TDA18250 driver.

Important APIs and types: defines register offsets `R00_ID1` through `R5C_AGC_DEBUG`, `TDA18250_NUM_REGS`, power states, IRQ masks for calibration/init/tune, and `struct tda18250_dev`.

Control flow: the implementation uses these symbols for regmap volatile ranges, init tables, power transitions, AGC programming, IF/RF programming, IRQ polling, and PLL adjustment.

State and persistence: `struct tda18250_dev` captures device configuration and runtime cache: mutex, frontend/client/regmap links, crystal frequency, IF values, current IF, variant flags, warm-init flag, and a register array that is not materially used by the current C file.

Dependencies and integration points: includes the public TDA18250 header. It is private to the tuner module.

Risks: the large flat register list has minimal field masks, so call sites must supply correct masks manually. IRQ constants combine multiple bits and are compared with equality-mask semantics in wait code. The unused `regs` member can mislead maintainers into assuming a software shadow exists.

Test signals: compile coverage for all register references, regmap volatile read behavior, IRQ mask polling tests, and review of power/standby register traces against hardware documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda18250_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda18271-common.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/tda18271-common.c

Purpose: shared low-level support for the TDA18271 analog/digital tuner: I2C gate selection, register read/write, default register initialization, standby programming, PLL calculation helpers, map-derived bitfield calculation, and debug printing.

Important APIs and functions: exported-to-module functions include `tda18271_read_regs`, `tda18271_read_extended`, `tda18271_write_regs`, `tda18271_init_regs`, `tda18271_charge_pump_source`, `tda18271_set_standby_mode`, `tda18271_calc_main_pll`, `tda18271_calc_cal_pll`, filter/map calculators, and `_tda_printk`. `__tda18271_write_regs` performs chunked writes and optional I2C bus locking.

Control flow: read helpers open the selected analog/digital gate, perform register reads, update the private register image, and preserve write-only extended bytes. Writes chunk the private register image according to `small_i2c`, optionally lock the I2C segment across multi-chunk operations, and close the gate. `tda18271_init_regs` writes a C1/C2-specific full register image, performs AGC setup, image rejection calibration for low/mid/high bands, synchronizes, and releases the bus. Calculation helpers look up PLL/filter values through maps and mutate the private register image without immediately writing every field.

State and persistence: all state lives in `struct tda18271_priv`: a 39-byte register shadow, selected gate/mode/role/version, output options, map layout, calibration state, and locks. Hardware state is synchronized from this shadow via explicit write calls.

Dependencies and integration points: depends on `tda18271-priv.h`, Linux I2C locking/transfer APIs, and frontend analog/digital I2C gate callbacks. It is used by `tda18271-fe.c` for init, calibration, tune, and standby.

Risks: `BUG_ON` is used for invalid write ranges, turning programming errors into kernel crashes. Many writes ignore return values during long calibration sequences. Gate selection depends on current mode when configured as auto; wrong mode can route I2C through the wrong demod bridge. Chunked writes and direct `__i2c_transfer` require careful bus locking.

Test signals: register trace comparison for C1 and C2 initialization, small-I2C chunk modes, analog vs digital I2C gate routing, read-extended write-only preservation, standby mode bit combinations, and map/PLL calculations over RF boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda18271-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda18271-fe.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/tda18271-fe.c

Purpose: main frontend-facing TDA18271 tuner implementation, covering attach/release, configuration, calibration, analog/digital tuning, AGC integration, standby, and cached frequency/bandwidth/IF reporting.

Important APIs and functions: exported entry is `tda18271_attach`. Tuner ops are `tda18271_init`, `tda18271_sleep`, `tda18271_set_params`, `tda18271_set_analog_params`, `tda18271_release`, `tda18271_set_config`, and getters. Internal calibration paths include `tda18271_ir_cal_init`, C1 RF tracking calibration, C2 RF tracking filter init/correction, power scan, thermometer read, and channel configuration.

Control flow: attach uses `hybrid_tuner_request_state` to share state per I2C adapter/address, configures role/gate/output/small-I2C options, identifies C1/C2 hardware, assigns maps, optionally initializes/calibrates immediately, and installs tuner ops. Digital tuning selects a standard-map row by delivery system and bandwidth, tri-states the analog demod if present, initializes the tuner, performs C1 or C2 RF tracking handling, then programs channel configuration and caches frequency/bandwidth/IF. Analog tuning maps V4L2 TV/radio standards to standard-map rows and reuses the same tune core. Sleep sets standby with configured loop-through/XTAL options.

State and persistence: shared state persists across multiple frontend users through the hybrid tuner list. `priv->lock` serializes init/tune/sleep hardware mutations; `tda18271_list_mutex` serializes attach/release. Calibration data and temperature baseline persist in `rf_cal_state`, `tm_rfcal`, and `cal_initialized`.

Dependencies and integration points: depends on common/map files, `tda8290.h` for LNA configuration enums, analog demod ops for gate/standby, frontend callbacks for AGC enable, and module parameters `debug` and `cal`.

Risks: the attach path dereferences `cfg->delay_cal` even though earlier setup allows `cfg` to be NULL, so callers likely must pass config despite the apparent optional API. Calibration is long, stateful, and has several ignored return values. Shared hybrid state means late attach configuration can override fields used by another frontend. External AGC callback behavior is board-specific.

Test signals: attach/release reference sharing, C1 and C2 ID detection, delayed vs startup calibration, module parameter override of calibration, digital tune for ATSC/DVB/ISDB/QAM, analog TV/radio standards, analog demod standby during digital tuning, and concurrent users on the same I2C address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda18271-fe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda18271-maps.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/tda18271-maps.c

Purpose: provides all frequency-to-register lookup tables and default standard maps for the TDA18271 C1/C2 tuner variants.

Important APIs and functions: public helpers are `tda18271_lookup_thermometer`, `tda18271_lookup_cid_target`, `tda18271_lookup_rf_band`, `tda18271_lookup_pll_map`, `tda18271_lookup_map`, and `tda18271_assign_map_layout`. Static data includes C1/C2 main and calibration PLL maps, RF calibration maps, band-pass/filter/gain/IR/temperature maps, RF tracking templates, and C1/C2 `tda18271_std_map` defaults.

Control flow: `tda18271_assign_map_layout` selects the C1 or C2 map layout after hardware ID detection, copies the default standard map into private state, and initializes RF calibration state from the template. Lookup functions scan ascending maximum-frequency tables, return selected values, and emit debug-map traces.

State and persistence: static maps are immutable driver data. Per-device mutable state is only populated by copying the selected standard map and RF calibration template into `struct tda18271_priv`.

Dependencies and integration points: depends on private TDA18271 state and debug macros. Common and frontend files consume these lookups for PLL programming, RF tracking calibration, power scans, temperature compensation, and standard-specific IF/AGC values.

Risks: map searches are linear and rely on zero-terminated sorted tables; bad ordering or missing terminators would produce wrong tuning. Some out-of-range conditions intentionally return `-ERANGE`, while C1 RF-cal out-of-range is expected in high bands. Tables are hardware-calibration data with little algorithmic validation in code review.

Test signals: boundary-frequency tests for every lookup table, C1 vs C2 layout assignment, standard-map values for analog and digital modes, RF-band template copy, and debug traces around max-frequency transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda18271-maps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda18271-priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/tda18271-priv.h

Purpose: private register definitions, state structure, debug macros, map types, and internal function prototypes for the TDA18271 driver.

Important APIs and types: defines register offsets for the 39-byte TDA18271 register file, `struct tda18271_rf_tracking_filter_cal`, PLL/version enums, opaque map layout, `struct tda18271_priv`, debug level bits, `tda_fail`, map type enum, and prototypes shared by common/maps/frontend files.

Control flow: this header ties the multi-file implementation together. The register constants index the shadow array, debug macros annotate map/register/calibration flow, and internal prototypes allow each compilation unit to call the shared lookup and hardware helpers.

State and persistence: `struct tda18271_priv` is the durable per-I2C-address state: register shadow, hybrid list node, I2C props, current mode/role/gate/version/options, board config, calibration state, selected maps, standard map, RF calibration table, lock, and cached IF/frequency/bandwidth.

Dependencies and integration points: includes kernel primitives, `tuner-i2c.h`, and the public TDA18271 header. It integrates with Linux DVB frontend state via `fe->tuner_priv`.

Risks: `tda_fail` references a local `priv` symbol, so it is only safe in functions that define that name. The shared private header exposes many internals across C files, increasing coupling. Debug macros can produce high-volume logs during calibration and map scanning.

Test signals: compile all three TDA18271 C files together, static analysis for `tda_fail` call sites, lock coverage around `tda18271_priv` mutations, and register-index validation against `TDA18271_NUM_REGS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda18271-priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda18271.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/tda18271.h

Purpose: public attach/configuration header for the TDA18271 analog/digital tuner.

Important APIs and types: defines `struct tda18271_std_map_item`, `struct tda18271_std_map`, role/gate/output/small-I2C/mode enums, `struct tda18271_config`, callback command `TDA18271_CALLBACK_CMD_AGC_ENABLE`, and `tda18271_attach` or disabled-driver stub.

Control flow: board drivers call `tda18271_attach(fe, addr, i2c, cfg)`. Config selects master/slave PLL role, analog/digital gate routing, output standby behavior, I2C chunk size, startup calibration policy, delayed register access, optional standard overrides, and board LNA/AGC integration.

State and persistence: no state is stored here. Standard-map overrides and config flags are copied or applied into `struct tda18271_priv` at attach/set_config time.

Dependencies and integration points: includes I2C and DVB frontend APIs. It is used directly by board drivers and by `tda8290.c` when it discovers a TDA18271 behind an analog demod bridge.

Risks: many config fields are optional by convention but materially affect hardware access ordering and calibration. Disabled-driver stub returns `NULL`, so callers must not assume attach success. Standard-map overrides only apply entries whose key fields sum nonzero, which can make intentional all-zero overrides impossible.

Test signals: board attach with master/slave roles, analog/digital gate choices, small-I2C modes, delayed calibration, standard-map overrides, disabled Kconfig builds, and AGC callback invocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda18271.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda827x.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/tda827x.c

Purpose: implements attach-style support for Philips/NXP TDA8275/TDA8275A tuner variants for digital and analog use.

Important APIs and functions: exported entry is `tda827x_attach`. Initial ops assume older TDA827X until `tda827x_probe_version` reads a byte and either finalizes old ops or replaces them with TDA827XA ops. Key tuning functions are `tda827xo_set_params`, `tda827xo_set_analog_params`, `tda827xa_set_params`, `tda827xa_set_analog_params`, sleep/init/getters, and LNA/AGC helpers.

Control flow: attach allocates private state, records address/adapter/config, installs initial old-tuner ops, and defers variant detection to first init/sleep. Digital tuning selects IF by bandwidth, chooses a frequency table row, computes divider `N`, writes register sequences, waits, adjusts charge pump, and caches frequency/bandwidth. The A variant adds DVB-C-specific tables, AGC reads, LNA gain switching, CP correction, and AGC freeze. Analog tuning maps V4L2 standard/radio mode to sound IF and low-pass selection, then writes variant-specific tuning sequences.

State and persistence: `struct tda827x_priv` stores I2C address/adapter, config pointer, analog IF and LP selection, and cached frequency/bandwidth. Variant selection mutates `fe->ops.tuner_ops` and may populate `cfg->agcf`.

Dependencies and integration points: depends on DVB frontend I2C gate callbacks, V4L2 analog parameters, `tda8290_lna` config from `tda8290.h`, and optional board callbacks in `struct tda827x_config`. Often attached by `tda8290.c` behind an analog IF demod bridge.

Risks: many analog write sequences ignore transfer return values. Initial variant probing is lazy, so failures can surface on first init/sleep rather than attach. LNA behavior depends on board callback and switch address correctness. Several waits are long fixed sleeps, making tune latency high.

Test signals: attach plus first init detecting 8275 vs 8275A, digital DVB-T/DVB-C tuning across frequency tables, analog standards and radio, LNA high/low switching paths, I2C-gate open/close traces, and error injection for tuner reads/writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda827x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda827x.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/tda827x.h

Purpose: public configuration and attach declaration for the TDA827x tuner driver.

Important APIs and types: defines `struct tda827x_config` with optional init/sleep callbacks, TDA8290 LNA configuration, switch I2C address, and an `agcf` callback slot populated by the tuner implementation. Declares `tda827x_attach` or a disabled-driver stub.

Control flow: board code or `tda8290.c` calls `tda827x_attach`; the implementation installs frontend tuner ops and stores the config pointer for later board callbacks and AGC/LNA behavior.

State and persistence: header owns no state. The `agcf` function pointer is mutable output from the driver, so config may be both input and callback handoff state.

Dependencies and integration points: includes I2C, DVB frontend, and `tda8290.h` for LNA enum values. This tight coupling reflects common TDA829x plus TDA827x combo hardware.

Risks: the config pointer must remain valid for the attachment lifetime. The disabled stub returns `NULL`. `agcf` as an output field can surprise callers expecting config to be immutable.

Test signals: build with TDA827x enabled/disabled, attach through both board code and TDA8290 discovery, callback invocation for init/sleep/AGC, and LNA switch address verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda827x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda8290.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/tda8290.c

Purpose: implements the Philips/NXP TDA8290/TDA8295 analog IF demodulator and manages companion tuner discovery/attachment for TDA8275/TDA8275A/TDA18271 combinations.

Important APIs and functions: exported entries are `tda829x_attach` and `tda829x_probe`. Analog demod ops differ for TDA8290 and TDA8295: set params, has_signal, standby, release, and I2C gate control. Internal helpers handle I2C bridge open/close, audio/easy-mode selection, gain/headroom adjustment, TDA8295 power/GPIO/AGC, tuner discovery, and companion tuner init.

Control flow: attach allocates `struct tda8290_priv`, probes for TDA8290 and TDA8295 IDs, installs analog ops, optionally disables the I2C gate, optionally powers up and finds a tuner behind the bridge, attaches TDA18271 or TDA827x based on tuner ID byte, names the combo, initializes IF and companion tuner, and returns the frontend. Analog set_params configures the demod for TV/radio standard, opens the demod I2C bridge, invokes companion tuner analog tuning, polls lock/AGC/ADC status, applies gain adjustments and SECAM-L deadlock recovery, closes the bridge, and sets IF AGC. Probe excludes TDA9887-like devices by repeated-byte behavior before ID-specific and legacy checks.

State and persistence: private state includes tuner I2C props, easy-mode byte, companion tuner address, version bitmask, TDA827x config, and optional TDA18271 standard map. Companion tuner state is stored through `fe->ops.tuner_ops` and released only if this module attached it.

Dependencies and integration points: depends on `tuner-i2c`, V4L2 analog standards, TDA827x and TDA18271 attach APIs, frontend analog ops, and optional board LNA config/callbacks. It often sits between bridge drivers and the actual RF tuner.

Risks: attachment can power/control TDA8295 before `priv->ver` is known if neither probe succeeds, though failure cleanup follows. Companion tuner discovery heuristics can default to address `0x60` when ambiguous. Many I2C helper sends ignore return values, making partial configuration hard to detect. Global static `tda829x_tda18271_config` is modified per attach, which is risky for multiple devices.

Test signals: probe distinction among TDA8290/TDA8295/TDA9887, attach with no tuner probing, discovery of TDA8275/TDA8275A/TDA18271, bridge open/close sequencing, analog TV and FM radio modes, signal/AGC adjustment paths, standby, release ownership, and multiple-device attach tests for shared static config behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda8290.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda8290.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/tda8290.h

Purpose: public header for TDA8290/TDA8295 analog IF demodulator attach/probe and LNA configuration.

Important APIs and types: defines `enum tda8290_lna`, `struct tda829x_config` with LNA config, tuner probing control, no-gate flag, and optional TDA18271 standard map. Declares `tda829x_probe` and `tda829x_attach` or disabled-driver stubs.

Control flow: bridge drivers can probe an I2C address or attach the analog demod. Config determines whether the driver searches for a companion tuner and whether analog I2C gate callbacks remain active.

State and persistence: no header-owned state. Config fields are copied into `struct tda8290_priv`, while the standard map pointer is passed through to TDA18271 attachment.

Dependencies and integration points: includes I2C, DVB frontend, and TDA18271 public map definitions. TDA827x also includes this header for the LNA enum.

Risks: `probe_tuner` uses inverted-looking constants where `TDA829X_PROBE_TUNER` is zero and `TDA829X_DONT_PROBE` is one; callers must initialize intentionally. Disabled stubs differ in log level and return values (`-EINVAL` vs `NULL`).

Test signals: Kconfig enabled/disabled builds, attach with probe and no-probe configs, no-I2C-gate operation, LNA enum behavior through TDA827x/TDA18271 paths, and external callers handling failed attach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda8290.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda9887.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/tda9887.c

Purpose: implements the NXP TDA9885/9886/9887 analog IF demodulator as an attach-style analog demod driver with shared hybrid state.

Important APIs and functions: exported entry is `tda9887_attach`. Analog demod ops are `tda9887_set_params`, `tda9887_standby`, `tda9887_tuner_status`, `tda9887_get_afc`, `tda9887_release`, and `tda9887_set_config`. Helpers map TV/radio norms to bytes, apply module/config overrides, perform I2C writes, dump status, and decode AFC.

Control flow: attach uses `hybrid_tuner_request_state` keyed by adapter/address, initializes standby on first instance, and installs analog ops. `set_params` records mode, audio mode, and standard, clears standby, and calls `tda9887_configure`. Configure zeroes the four-byte write buffer, selects a norm table row or radio mono/stereo row, defaults output ports inactive, applies driver config flags and module parameters, optionally forces audio mute for standby, writes four bytes over I2C, and optionally reads status for debug. Standby sets a flag and reconfigures with forced mute.

State and persistence: shared `struct tda9887_priv` stores I2C props, hybrid list node, last written data bytes, config bitmask, mode/audmode/std, and standby flag. Hardware state is the last four-byte programming sequence; software retains it for status dumps.

Dependencies and integration points: depends on `tuner-i2c`, V4L2 standards, media tuner config flags from `<media/tuner.h>`, and DVB analog demod ops. It can coexist with other frontend components through `fe->analog_demod_priv`.

Risks: unsupported TV norms return an error from `tda9887_set_tvnorm`, but configure continues writing a mostly default/muted buffer. Global module parameters override board config and affect all devices. I2C write/read return values are logged but not propagated through set_params/standby. Hybrid shared state means config changes on one frontend affect other users of the same chip.

Test signals: attach/release reference sharing, norm selection for PAL/SECAM/NTSC and FM mono/stereo, config and module-parameter overrides, standby forced mute, AFC reporting in radio mode, debug read/write dumps, and I2C failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda9887.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda9887.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/tda9887.h

Purpose: public attach declaration for the TDA9885/6/7 analog IF demodulator.

Important APIs and types: declares `tda9887_attach(struct dvb_frontend *fe, struct i2c_adapter *i2c_adap, u8 i2c_addr)` when reachable and a disabled-driver inline stub otherwise.

Control flow: board drivers call attach to install `analog_demod_ops` into the frontend and bind shared state to `fe->analog_demod_priv`.

State and persistence: no state is defined here. The implementation allocates or shares state through the hybrid tuner instance list.

Dependencies and integration points: includes I2C and DVB frontend APIs. The demod is configured later through frontend analog ops and tuner config flags.

Risks: the disabled stub returns `NULL`, so callers must check attach success. This header exposes no config structure; runtime configuration is performed later via `analog_ops.set_config`.

Test signals: enabled/disabled Kconfig builds, board attach calls, subsequent analog ops availability, and failure handling when the module is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tda9887.h -->
