# Research: subset-b-004195

Grouped research report for Linux media tuner and USB media build files. Each section preserves the original source path and is intended to be split into the matching source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tea5761.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/tea5761.c

Purpose: implements the Philips TEA5761HN FM radio tuner as a DVB tuner-ops provider. It is a narrow analog-radio driver: attach validates the chip over I2C, allocates `struct tea5761_priv`, stores the adapter/address/name in `tuner_i2c_props`, and copies a static `dvb_tuner_ops` table into the frontend.

Important APIs and functions: exported `tea5761_attach()` and `tea5761_autodetection()` are the integration surface. Tuner callbacks include `set_radio_freq()`, `set_radio_sleep()`, `tea5761_get_frequency()`, `tea5761_get_status()`, `tea5761_get_rf_strength()`, and `tea5761_release()`. Internal helpers include `__set_radio_freq()`, `tea5761_read_status()`, `tea5761_signal()`, `tea5761_stereo()`, and optional debug dumping via `tea5761_status_dump()`.

Control flow: `tea5761_attach()` calls autodetection, allocates state, initializes I2C properties, then installs ops. Frequency changes clear standby and call `__set_radio_freq()`, which builds a 7-byte control payload, sets power-up or mute bits depending on `priv->standby`, applies mono/stereo mode, calculates the PLL divider from V4L2 62.5 Hz frequency units, sends the buffer with `tuner_i2c_xfer_send()`, and caches `priv->frequency` in Hz-like tuner units. Sleep sets standby and reuses the same programming path with mute/power-down bits. Status reads 16 bytes and derives lock from level and stereo from the TUNCHECK stereo bit.

State and persistence: state is entirely in `tea5761_priv`: current frequency, standby flag, and I2C properties. There is no firmware, no persistent storage, and no shared hybrid-instance list. Release frees `fe->tuner_priv`.

Dependencies and integration: uses Linux I2C, V4L2 tuner audio mode constants, `media/tuner.h`, `dvb_frontend`, and local `tuner-i2c.h`. It is enabled through `CONFIG_MEDIA_TUNER_TEA5761` and referenced by tuner type metadata in `tuner-types.c`.

Risks and test signals: detection depends on fixed manufacturer/chip ID bytes. I2C errors are mostly logged and frequency set returns success even if writes fail, so runtime tests should check dmesg and readback status. Frequency math and unit conversion are sensitive; useful tests are attach probe, tune FM stereo/mono stations, sleep/resume mute behavior, `get_frequency`, lock/stereo status, and RF-strength reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tea5761.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tea5761.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/tea5761.h

Purpose: public attach/autodetection header for the TEA5761 FM tuner driver. It lets bridge and tuner-core code call the TEA5761 implementation only when the Kconfig symbol is reachable.

Important APIs and types: declares `tea5761_autodetection(struct i2c_adapter *i2c_adap, u8 i2c_addr)` and `tea5761_attach(struct dvb_frontend *fe, struct i2c_adapter *i2c_adap, u8 i2c_addr)`. It includes `linux/i2c.h` and `media/dvb_frontend.h` because callers pass those core kernel objects directly.

Control flow and integration: under `IS_REACHABLE(CONFIG_MEDIA_TUNER_TEA5761)`, callers link to the real functions in `tea5761.c`. Otherwise, inline stubs log that the driver is disabled, return `-EINVAL` for autodetection, and return `NULL` for attach. This allows callers to compile cleanly regardless of whether the tuner is built in, modular, or disabled.

State and persistence: no local state is defined in the header. All device state lives in `tea5761.c` after successful attach.

Dependencies: depends on the media tuner Kconfig symbol, kernel printk, I2C adapter type, and DVB frontend type. The header is part of the tuner attachment contract used by board drivers.

Risks and test signals: stale prototypes or Kconfig mismatches surface as link or attach failures. Tests should build with TEA5761 enabled, modular, and disabled to validate both real and stub paths; disabled-driver probes should produce an expected log and fail gracefully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tea5761.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tea5767.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/tea5767.c

Purpose: implements the Philips TEA5767 FM radio tuner. It supports analog radio tuning, standby, signal/stereo status, autodetection, and runtime configuration of TEA5767 control bits.

Important APIs and functions: exported `tea5767_attach()` and `tea5767_autodetection()` are public. `tea5767_tuner_ops` wires `.set_analog_params`, `.set_config`, `.sleep`, `.release`, `.get_frequency`, `.get_status`, and `.get_rf_strength`. Internal helpers include `set_radio_freq()`, `tea5767_standby()`, `tea5767_read_status()`, `tea5767_signal()`, `tea5767_stereo()`, and `tea5767_status_dump()`.

Control flow: attach allocates `tea5767_priv`, sets default control fields (`HIGH_LO_32768`, both ports high, high-cut, stereo-noise, Japan band), initializes I2C properties, and installs ops. Tuning builds the TEA5767 five-byte register image from `analog_parameters`: port bits, mono mode, high-cut/noise/soft-mute/band/deemphasis/pllref bits, then a PLL divider chosen by crystal and high/low injection mode. The driver writes the register image through `tuner_i2c_xfer_send()`, optionally reads back and dumps status when debugging, and caches frequency. Standby writes a fixed 87.5 MHz payload with standby bit set.

State and persistence: `tea5767_priv` stores I2C properties, last frequency, and `struct tea5767_ctrl`. The `.set_config` callback blindly copies caller-supplied control data into `priv->ctrl`; no firmware or nonvolatile state exists.

Dependencies and integration: uses local `tuner-i2c.h`, public `tea5767.h`, Linux I2C, V4L2 audio mode constants, and DVB tuner ops. Autodetection reads status bytes and rejects TV tuners that return all-equal bytes or nonzero chip ID fields.

Risks and test signals: the `.set_config` path assumes the caller supplies a valid `struct tea5767_ctrl`; bad crystal or injection settings directly produce wrong RF frequencies. I2C write errors are logged but do not fail tuning. Tests should cover attach/default config, all `xtal_freq` modes where hardware permits, mono/stereo, standby, autodetection false positives, RF strength, and `get_status` stereo/lock behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tea5767.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tea5767.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/tea5767.h

Purpose: public interface for TEA5767 attach, autodetection, and board-specific control configuration.

Important APIs and types: `enum tea5767_xtal` selects low/high LO injection with either 32.768 kHz or 13 MHz reference. `struct tea5767_ctrl` carries bitfields for port outputs, high-cut, stereo-noise control, soft mute, Japan band, 75 us deemphasis, PLL reference, and `xtal_freq`. It declares `tea5767_autodetection()` and `tea5767_attach()`.

Control flow and integration: when `CONFIG_MEDIA_TUNER_TEA5767` is reachable, callers use the real implementation. Otherwise inline stubs log disabled-driver messages and fail. Callers may pass `struct tea5767_ctrl` through the tuner `.set_config` operation after attach.

State and persistence: this header defines configuration shape but stores no state. The implementation copies the config into per-device private memory.

Dependencies: includes Linux I2C and DVB frontend headers. It is coupled to V4L2/media bridge drivers that need to attach an FM tuner at a known I2C address.

Risks and test signals: bitfield layout is compiler-defined but only used inside the kernel build as a C struct, not a wire ABI. Tests should compile all Kconfig variants and verify board code passes initialized `tea5767_ctrl` data before tuning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tea5767.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tua9001.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/tua9001.c

Purpose: implements the Infineon TUA9001 silicon tuner as a modern `i2c_driver` using regmap. It attaches to a DVB frontend through platform data and provides DVB-T tuning over I2C plus bridge callbacks for hardware enable/reset pins.

Important APIs and functions: the module registers `tua9001_driver` with `.probe`, `.remove`, and `i2c_device_id` `"tua9001"`. Tuner ops include `tua9001_init()`, `tua9001_sleep()`, `tua9001_set_params()`, and `tua9001_get_if_frequency()`. Private state is `struct tua9001_dev`; register/value initialization uses `struct tua9001_reg_val`.

Control flow: probe receives `tua9001_platform_data`, allocates private state, creates an 8-bit register/16-bit value regmap, invokes frontend callbacks to enable CEN, disable RXEN, and hold RESETN, then installs tuner ops. Init toggles RESETN through the callback and writes a fixed initialization table. Set-params accepts only `SYS_DVBT`, maps bandwidth 5/6/7/8 MHz to register `0x04`, calculates register `0x1f` from `(frequency - 150 MHz) * 48 / 1 MHz`, disables RXEN, writes both registers, then re-enables RXEN. Sleep asserts RESETN through callback. IF is reported as zero because this is a zero-IF tuner.

State and persistence: state is per-I2C-client memory: frontend pointer, client pointer, and regmap. There is no firmware and no persistent state; removal disables CEN through callback and frees private memory.

Dependencies and integration: depends on `regmap`, Linux I2C driver core, DVB frontend callbacks, and `tua9001.h` command values. The bridge driver must provide platform data and implement CEN/RXEN/RESETN callbacks.

Risks and test signals: null or malformed platform data would break probe assumptions. Unsupported delivery systems or bandwidths return `-EINVAL`. Frequency below 150 MHz would underflow the unsigned arithmetic path, though tuner ops advertise a 170-862 MHz range. Tests should cover probe/remove GPIO callback ordering, init register writes, DVB-T bandwidth selection, RXEN gating around retune, IF frequency 0, and regmap write failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tua9001.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tua9001.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/tua9001.h

Purpose: public board-facing header for the TUA9001 tuner. It defines platform data and callback command IDs that bridge drivers use to attach and control tuner-side pins.

Important APIs and types: `struct tua9001_platform_data` carries the target `struct dvb_frontend *`. Command constants are `TUA9001_CMD_CEN`, `TUA9001_CMD_RESETN`, and `TUA9001_CMD_RXEN`, matching chip-enable, reset, and receiver-enable lines.

Control flow and integration: a bridge creates an I2C client for `"tua9001"` with this platform data. During probe and tuner operations, `tua9001.c` invokes `fe->callback(adapter, DVB_FRONTEND_COMPONENT_TUNER, command, value)` with these command IDs. The header documents expected pin semantics.

State and persistence: no state is stored here; it only defines the attach contract. Runtime pin state is external to the tuner driver and owned by the bridge callback implementation.

Dependencies: includes `media/dvb_frontend.h`. It is consumed by TUA9001 bridge glue and by the private implementation header.

Risks and test signals: callback command meanings must stay synchronized between bridge and tuner driver. Tests should verify each command changes the intended GPIO/regulator path and that missing callbacks still leave the I2C register path usable where hardware permits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tua9001.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tua9001_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/tua9001_priv.h

Purpose: private implementation header for the TUA9001 driver. It keeps local register-pair and device-state definitions out of the public board interface.

Important APIs and types: `struct tua9001_reg_val` stores an 8-bit register and 16-bit value for initialization and retune tables. `struct tua9001_dev` stores the attached `dvb_frontend`, `i2c_client`, and `regmap`.

Control flow and integration: included only by `tua9001.c`. The register-pair type feeds `regmap_write()` loops in init and set-params; the device struct is allocated at probe, stored as I2C client data, and assigned to `fe->tuner_priv`.

State and persistence: `tua9001_dev` is the complete runtime state for this driver. It is allocated on probe and freed on remove; regmap lifetime is devm-managed.

Dependencies: includes public `tua9001.h`, `linux/math64.h` for frequency calculations, and `linux/regmap.h` for register access.

Risks and test signals: because this is private, risks are mainly lifetime and ownership: `fe->tuner_priv` and I2C client data must both refer to valid memory until remove/release. Tests should use probe/remove and tune failure injection to ensure no dangling state is used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tua9001_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tuner-i2c.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/tuner-i2c.h

Purpose: shared helper header for legacy media tuner drivers using simple I2C transactions and optional hybrid-tuner state sharing.

Important APIs and types: `struct tuner_i2c_props` contains I2C address, adapter, instance count, and name. Inline transfer helpers are `tuner_i2c_xfer_send()`, `tuner_i2c_xfer_recv()`, and `tuner_i2c_xfer_send_recv()`, all wrapping `i2c_transfer()` and returning byte counts on success. Logging macros (`tuner_warn`, `tuner_info`, `tuner_err`, `tuner_dbg`) assume a local `priv->i2c_props` and module-level `debug`.

Control flow: send/recv helpers build one or two `struct i2c_msg` objects and normalize successful transfer counts to requested byte lengths. Hybrid macros scan a caller-provided global list for matching adapter ID and I2C address; they either increment the existing state's count or allocate/link a new state. Release decrements the count and frees/unlinks when it reaches zero.

State and persistence: this header does not own state directly, but the hybrid macros manage lifetime for driver private objects containing `hybrid_tuner_instance_list` and `i2c_props`. The state is in memory only and shared across analog/digital frontend attachments.

Dependencies and integration: depends on Linux I2C, slab allocation helpers, list heads supplied by each driver, and consistent private struct layout. Used by TEA576x, tuner-simple, and Xceive drivers.

Risks and test signals: macro-based lifetime management is not type-safe and requires external locking. Adapter-ID/address matching can alias devices if reused incorrectly. Transfer helpers return negative errors or transfer counts, so callers must compare with exact expected byte lengths. Tests should cover shared attach/release reference counts, I2C error propagation, logging format, and concurrent attach under the driver's list mutex.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tuner-i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tuner-simple.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/tuner-simple.c

Purpose: implements a generic "simple four-control-byte" tuner driver for many analog and hybrid TV/FM tuner cans. It converts V4L2 analog radio/TV and DVB frontend requests into model-specific PLL bytes using tables from `tuner-types.c`.

Important APIs and functions: exported `simple_tuner_attach()` installs `simple_tuner_ops`. Main callbacks are `simple_init()`, `simple_sleep()`, `simple_set_params()` for analog/radio, `simple_dvb_set_params()`, `simple_dvb_calc_regs()`, `simple_get_frequency()`, `simple_get_bandwidth()`, `simple_get_status()`, `simple_get_rf_strength()`, and `simple_release()`. Key helpers are `simple_tuner_params()`, `simple_config_lookup()`, `simple_std_setup()`, `simple_set_tv_freq()`, `simple_set_radio_freq()`, `simple_dvb_configure()`, `simple_set_dvb()`, `simple_radio_bandswitch()`, and `simple_post_tune()`.

Control flow: attach validates tuner type, optionally probes the I2C address through the frontend gate, obtains shared state with `hybrid_tuner_request_state()`, installs ops, and copies the tuner name from `tuners[type]`. Analog TV tuning chooses PAL/SECAM/NTSC params, computes IF offset, looks up range config/cb bytes, applies standard-specific and RF-input tweaks, optionally configures a TDA9887 demod through `i2c_clients_command()`, writes four bytes, and performs model-specific post-tune actions. Radio tuning selects a radio-capable params entry, adds the configured radio IF, chooses a 50 kHz PLL step, sets band-switch bytes, configures TDA9887 FM flags if present, writes four bytes, and may write an AUX byte. Digital tuning uses frontend delivery system/bandwidth/frequency to compute model-specific DVB bytes and writes them after putting the analog demod in standby and opening the I2C gate.

State and persistence: `tuner_simple_priv` stores instance number, last divider, I2C props, shared-list node, tuner type/table pointer, cached frequency, bandwidth, and radio-mode flag. Module parameters `offset`, `atv_input[]`, and `dtv_input[]` alter tuning globally. State is in memory and reference-counted for hybrid users.

Dependencies and integration: depends on `media/tuner.h`, `media/v4l2-common.h`, `media/tuner-types.h`, local `tuner-i2c.h`, and `tuner-simple.h`. It integrates with analog demod standby hooks, I2C gates, TDA9887 private config commands, and the exported `tuners[]` database.

Risks and test signals: this is dense table-driven legacy hardware code; regressions usually appear as wrong band-switch bytes, wrong IF offsets, or shared-state lifetime issues. Some I2C write failures are logged but not surfaced. Tests should cover representative PAL/NTSC/SECAM analog tuners, radio-capable tuners, digital hybrid tuners with `calc_regs`, module RF-input overrides, TDA9887 config emission, invalid tuner type, no-I2C-adapter calc path, and attach/release reference counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tuner-simple.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tuner-simple.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/tuner-simple.h

Purpose: public attach header for the generic simple tuner driver.

Important APIs: declares `simple_tuner_attach(struct dvb_frontend *fe, struct i2c_adapter *i2c_adap, u8 i2c_addr, unsigned int type)` when `CONFIG_MEDIA_TUNER_SIMPLE` is reachable. The `type` argument indexes the `tuners[]` table in `tuner-types.c`.

Control flow and integration: callers attach a frontend to a simple tuner by providing I2C adapter/address and tuner type. If disabled by Kconfig, the inline stub logs a warning and returns `NULL`, preserving compile compatibility for board drivers.

State and persistence: no state is defined in the header. Runtime state is allocated and shared by `tuner-simple.c`.

Dependencies: includes Linux I2C and DVB frontend headers. It depends indirectly on `media/tuner-types.h` constants used by callers for the `type` argument.

Risks and test signals: the most important contract is that board code passes a valid tuner type. Build tests should cover enabled and disabled Kconfig paths; runtime tests should confirm disabled stubs fail gracefully and enabled attach copies expected tuner ops and names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tuner-simple.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tuner-types.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/tuner-types.c

Purpose: central device-type database for simple media tuner cans. It provides frequency ranges, config bytes, control bytes, IF parameters, optional init/sleep bytes, and names for `tuner-simple.c` and tuner-core users.

Important APIs and data: exports `const struct tunertype tuners[]` and `unsigned const int tuner_count`. The file defines many `static const struct tuner_range` arrays and `static const struct tuner_params` arrays for PAL, NTSC, SECAM, radio, and digital variants. Shared initialization arrays such as `tua603x_agc103` and `tua603x_agc112` encode AUX-byte sequences for selected TUA603x-based tuners.

Control flow: there is no active code beyond module exports. Runtime behavior is data-driven: `simple_tuner_attach()` selects `tuners[type]`; tuning code chooses a `tuner_params` entry matching requested analog/digital/radio mode; `simple_config_lookup()` picks the first frequency range whose limit covers the target; then `tuner-simple.c` uses the stored config/cb/IF/flags to build I2C payloads and optional TDA9887 settings.

State and persistence: all data is static read-only except compound literal sleepdata embedded in tuner entries. No mutable runtime state is stored here.

Dependencies and integration: includes `media/tuner.h` and `media/tuner-types.h`, which define tuner IDs and struct layouts. Special entries for TEA5761, TEA5767, XC2028, XC4000, XC5000, TDA8290, TDA9887, SI2157, and MT20xx act as database names while implementation lives in separate drivers.

Risks and test signals: this file is a high-blast-radius lookup table. Any wrong range limit, byte, IF, step size, or tuner ID mapping retunes hardware incorrectly. The use of compile-time float constants depends on constant folding into integers. Tests should compile-check table sizes against enum IDs, attach several known tuner IDs, verify range selection at boundaries, validate digital `stepsize/min/max/iffreq`, and compare known board behavior after any table edit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/tuner-types.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/xc2028-types.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/xc2028-types.h

Purpose: internal firmware type and standard bit definitions shared by Xceive XC2028/XC3028 and XC4000 code. The comment explicitly says it should not be included outside XC2028-style firmware handling, though XC4000 also uses it.

Important APIs and constants: defines firmware type bits such as `BASE`, `F8MHZ`, `MTS`, `D2620`, `D2633`, `DTV6`, `DTV7`, `DTV78`, `DTV8`, `QAM`, `FM`, `INPUT1`, `INPUT2`, `LCD`, `NOGD`, `INIT1`, `SCODE`, and `HAS_IF`. It also defines masks `BASE_TYPES`, `DTV_TYPES`, `STD_SPECIFIC_TYPES`, and `SCODE_TYPES`. It adds internal V4L2 standard/audio masks such as `V4L2_STD_SECAM_K3`, A2/NICAM/AM/BTSC/EIAJ bits, `V4L2_STD_AUDIO`, and combinations for PAL/SECAM audio variants.

Control flow and integration: the Xceive drivers use these bits to parse firmware containers, seek exact or best matching firmware images, decide which base/std/scode segments to load, and modify analog standard masks based on audio options.

State and persistence: no state. The constants shape firmware state machines in `xc2028.c` and `xc4000.c`.

Dependencies: relies on V4L2 standard bit layout from media headers. It is tightly coupled to the binary firmware file format and selection logic.

Risks and test signals: bit collisions or incorrect masks can cause wrong firmware selection. Because some standard bits extend above regular V4L2 masks, tests should cover firmware matching for analog PAL/NTSC/SECAM variants, audio-specific selections, DTV bandwidth types, SCODE with and without `HAS_IF`, and builds with all including drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/xc2028-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/xc2028.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/xc2028.c

Purpose: firmware-driven driver for Xceive XC2028/XC3028 tuners supporting analog TV, FM radio, and digital TV. It manages firmware loading, SCODE selection, shared hybrid instances, power management, and frequency programming.

Important APIs and functions: exported `xc2028_attach()` installs `xc2028_dvb_tuner_ops`. Key callbacks are `xc2028_set_config()`, `xc2028_set_analog_freq()`, `xc2028_set_params()`, `xc2028_sleep()`, `xc2028_get_frequency()`, `xc2028_signal()`, `xc2028_get_afc()`, and release. Firmware core functions include `load_all_firmwares()`, `seek_firmware()`, `load_firmware()`, `load_scode()`, `check_firmware()`, `check_device_status()`, and `generic_set_freq()`.

Control flow: attach obtains/refcounts shared state for adapter/address, initializes the mutex/default max transfer length, installs ops, and optionally applies caller control. `xc2028_set_config()` copies `struct xc2028_ctrl`, selects firmware name, and starts asynchronous `request_firmware_nowait()`; callback parses the firmware header and image table into memory. Tuning calls `generic_set_freq()`: it locks, ensures matching firmware via `check_firmware()`, optionally sends analog soft reset, computes digital frequency offsets by firmware/bandwidth, writes RF frequency command, invokes bridge clock-reset callback, writes the divisor, and caches frequency. Digital set-params maps DVB-T/T2/ATSC bandwidth/demod options to DTV firmware type bits and optional SCODE IF. Analog set-params maps radio to `FM` plus input and TV standards to standard-specific firmware with optional parsed audio mask.

State and persistence: `struct xc2028_data` stores I2C props, current frequency, state enum, firmware file name/table/version, hardware IDs, control flags, current firmware properties, and a mutex. Firmware is retained in memory and freed only when the last hybrid instance releases it. No persistent storage exists; firmware files are external runtime dependencies.

Dependencies and integration: depends on Linux firmware loader, I2C, V4L2 standards, DVB frontend property cache, local `tuner-i2c.h`, public `xc2028.h`, and `xc2028-types.h`. Bridge callbacks handle tuner reset, reset clock, and I2C flush.

Risks and test signals: asynchronous firmware loading creates waiting/error states; callers must handle tuning before firmware is ready. Firmware parsing validates sizes but corrupt firmware can disable the device state. Wrong `ctrl.demod`, SCODE table, bandwidth, or audio option can select unusable firmware. Tests should cover firmware present/missing/corrupt, attach sharing and release, analog TV standards, FM input, DVB-T 6/7/8 MHz and ATSC, sleep with and without power management disabled, signal/AFC reads, and callback failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/xc2028.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/xc2028.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/xc2028.h

Purpose: public configuration and attach interface for Xceive XC2028/XC3028 tuner drivers.

Important APIs and types: defines default firmware names `XC2028_DEFAULT_FIRMWARE` and `XC3028L_DEFAULT_FIRMWARE`, demod IF constants (`XC3028_FE_*`), `enum firmware_type`, `struct xc2028_ctrl`, and `struct xc2028_config`. `xc2028_ctrl` carries firmware filename, max I2C length, sleeps, SCODE table, MTS/input/bandwidth/power/read flags, demod IF, and firmware type. It declares `xc2028_attach()`.

Control flow and integration: board drivers populate `xc2028_config` with I2C adapter/address and optional control block, then call attach. The implementation copies the control data and can request firmware immediately. Callback command IDs `XC2028_TUNER_RESET`, `XC2028_RESET_CLK`, and `XC2028_I2C_FLUSH` define bridge callback behavior.

State and persistence: no header state; runtime state is allocated in `xc2028.c`. Firmware name points to external firmware files loaded by request_firmware.

Dependencies: includes `media/dvb_frontend.h`; relies on Kconfig `CONFIG_MEDIA_TUNER_XC2028` for real vs stub attach.

Risks and test signals: invalid `max_len`, demod IF, firmware filename, or callback support affects tuning. Tests should build enabled/disabled paths, verify default firmware names are packaged, and validate board callback implementations for reset/clock/flush commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/xc2028.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/xc4000.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/xc4000.c

Purpose: firmware-driven Xceive XC4000/XC4100 silicon tuner driver for analog TV, FM radio, ATSC/QAM, and DVB-T/T2-style digital tuning.

Important APIs and functions: exported `xc4000_attach()` installs `xc4000_tuner_ops`. Main callbacks include `xc4000_init()`, `xc4000_sleep()`, `xc4000_set_params()`, `xc4000_set_analog_params()`, `xc4000_get_frequency()`, `xc4000_get_bandwidth()`, `xc4000_get_status()`, `xc4000_get_signal()`, and release. Firmware helpers include `xc4000_fwupload()`, `seek_firmware()`, `load_firmware()`, `load_scode()`, and `check_firmware()`. Register helpers include `xc_write_reg()`, `xc4000_readreg()`, `xc_set_tv_standard()`, `xc_set_signal_source()`, and `xc_tune_channel()`.

Control flow: attach creates or reuses shared state, applies config defaults/overrides, reads product ID to distinguish firmware-loaded vs unloaded devices, installs ops, and loads firmware for first instances. Firmware upload tries a new default file then falls back to an older one, parses an XC firmware image table, and stores segments in memory. Digital tuning maps delivery system and bandwidth to RF mode, frequency offset, `video_standard`, and firmware type (`DTV6/7/78/8`), checks firmware, sets signal source and video/audio mode registers, writes optional amplitude/smoothed-CVBS registers, and tunes RF. Analog tuning normalizes V4L2 standard/audio options into one of 24 `xc4000_standard` entries, loads matching firmware/SCODE, programs source/standard/amplitude, and tunes. Sleep can power down and mark current firmware as invalid so later tuning reloads.

State and persistence: `xc4000_priv` stores I2C props, shared-list node, firmware table, IF, current frequency/offset, bandwidth, video standard, RF mode, default power management, amplitude/CVBS options, firmware version/current firmware, hardware IDs, write-error ignore flag, and lock. Firmware remains in memory for shared instances but is not persisted.

Dependencies and integration: uses firmware loader, I2C, V4L2/DVB frontend APIs, `tuner-i2c.h`, `xc4000.h`, and `xc2028-types.h`. Tuner reset is delegated through the frontend callback `XC4000_TUNER_RESET`.

Risks and test signals: firmware file availability and correctness are critical. Some I2C write errors are intentionally ignored during firmware load to tolerate clock stretching. Analog audio standard module parameters change firmware and mode selection. Tests should cover product ID paths, firmware fallback, corrupt firmware, shared attach/release, digital delivery systems/bandwidth offsets, analog PAL/NTSC/SECAM/FM, sleep/power-management behavior, signal scaling, and callback reset failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/xc4000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/xc4000.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/xc4000.h

Purpose: public attach/configuration header for the Xceive XC4000 tuner.

Important APIs and types: `struct xc4000_config` carries I2C address, default power-management behavior, DVB-T amplitude override, smoothed-CVBS option, and DVB-T IF in kHz. It defines callback command `XC4000_TUNER_RESET` and declares `xc4000_attach()`.

Control flow and integration: bridge drivers call `xc4000_attach(fe, i2c, cfg)`. The implementation stores selected config fields in shared private state, probes product ID, loads firmware, and installs tuner ops. Reset callbacks let board-specific GPIO code reset the tuner without exposing bridge internals.

State and persistence: no runtime state in the header. Config values become in-memory fields inside `xc4000_priv`; firmware files are external.

Dependencies: includes `linux/firmware.h` for firmware-related declarations and forward-declares `dvb_frontend` and `i2c_adapter`. Kconfig controls real vs inline disabled stub.

Risks and test signals: callers must provide a valid config pointer and I2C address. Build tests should cover enabled/disabled Kconfig; integration tests should verify reset callback wiring, IF override, power-management option, amplitude option, and required firmware packaging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/xc4000.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/xc5000.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/xc5000.c

Purpose: firmware-driven Xceive XC5000/XC5000C tuner driver supporting analog TV, FM radio, multiple digital delivery systems, suspend/resume, and delayed sleep.

Important APIs and functions: exported `xc5000_attach()` installs `xc5000_tuner_ops`. Main callbacks include `xc5000_init()`, `xc5000_sleep()`, `xc5000_suspend()`, `xc5000_resume()`, `xc5000_set_config()`, `xc5000_set_digital_params()`, `xc5000_set_analog_params()`, `xc5000_get_frequency()`, `xc5000_get_if_frequency()`, `xc5000_get_bandwidth()`, `xc5000_get_status()`, `xc5000_get_rf_strength()`, and release. Firmware/control helpers include `xc5000_assign_firmware()`, `xc_load_fw_and_init_tuner()`, `xc5000_fwupload()`, `xc5000_is_firmware_loaded()`, `xc_initialize()`, `xc_set_tv_standard()`, `xc_set_signal_source()`, `xc_set_rf_frequency()`, `xc_set_IF_frequency()`, and `xc_tune_channel()`.

Control flow: attach creates or reuses hybrid state, applies IF/xtal/radio/chip/output config, checks product ID, initializes delayed sleep work, and installs ops. Init and every tune path call `xc_load_fw_and_init_tuner()` as needed. Firmware selection depends on chip ID: XC5000A uses `dvb-fe-xc5000-1.6.114.fw`; XC5000C uses `dvb-fe-xc5000c-4.1.30.7.fw`. Firmware size is validated, upload is retried up to five times, optional checksum/init status and PLL lock are checked, and default cable mode is set. Digital tuning maps delivery system and bandwidth to RF mode, frequency offset, and standard, then programs source, standard, IF, output amplitude, and RF. Analog TV selects a standard from V4L2 masks; radio uses configured FM input and output amplitude.

State and persistence: `xc5000_priv` stores I2C props, shared-list node, IF/xtal, current frequency/offset, bandwidth, video standard, mode, RF mode, radio input, output amp, chip ID, PLL/status support flags, frontend pointer, delayed work, and `inited`. Firmware is not stored after upload; the chip retains it until reset/power loss.

Dependencies and integration: uses Linux firmware loader, delayed workqueue, I2C, DVB/V4L2 APIs, local `tuner-i2c.h`, and public `xc5000.h`. Reset/powerdown is delegated to frontend callback `XC5000_TUNER_RESET`.

Risks and test signals: firmware file size is hard-coded and must match packaged blobs. Delayed sleep can race with tuning unless cancellation paths work. Product ID and PLL checks decide whether firmware reloads. Tests should cover both chip IDs, firmware missing/wrong-size/retry paths, digital ATSC/DVB-C/DVB-T/T2/ISDB-T/DMBTH bandwidth mapping, analog TV and FM inputs, sleep/suspend/resume delayed work, output amplitude override, and shared attach/release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/xc5000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/xc5000.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/xc5000.h

Purpose: public attach/configuration header for Xceive XC5000 and XC5000C tuners.

Important APIs and types: defines chip IDs `XC5000A` and `XC5000C`, `struct xc5000_config`, callback command `XC5000_TUNER_RESET`, radio input constants (`XC5000_RADIO_*`), and `xc5000_attach()`. Config includes I2C address, IF kHz, radio input, crystal kHz, output amplitude, and chip ID.

Control flow and integration: bridge drivers call `xc5000_attach(fe, i2c, cfg)`, then may use `.set_config` to update IF/radio/output fields. The implementation chooses firmware based on chip ID and uses bridge callbacks for reset during sleep/suspend.

State and persistence: no header state. Config values are copied into shared private state and influence firmware selection and tuning.

Dependencies: includes `linux/firmware.h` and forward-declares DVB frontend/I2C adapter. Kconfig controls real vs disabled-stub attach.

Risks and test signals: incorrect chip ID selects the wrong firmware blob; missing radio input prevents FM mode. Tests should build both Kconfig paths and validate board configs for IF, xtal, output amplitude, chip ID, radio input, and reset callback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/xc5000.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/usb/Kconfig

Purpose: top-level Kconfig menu for USB media adapters in the Linux media subsystem.

Important entries: `menuconfig MEDIA_USB_SUPPORT` is visible when `USB && MEDIA_SUPPORT` and gates the nested USB media driver menus. Conditional blocks source Kconfig files for webcams, analog TV USB devices, analog/digital TV devices, digital TV USB devices requiring I2C, combined webcam/TV devices, and SDR devices.

Control flow: if USB media support is enabled, the file emits category comments and `source` statements based on higher-level media feature symbols: `MEDIA_CAMERA_SUPPORT`, `MEDIA_ANALOG_TV_SUPPORT`, `MEDIA_DIGITAL_TV_SUPPORT`, `I2C`, and `MEDIA_SDR_SUPPORT`. The AirSpy Kconfig is sourced only under SDR support.

State and persistence: Kconfig choices persist in the kernel `.config`, not in this file at runtime.

Dependencies and integration: integrates USB media subdirectories with the wider media menu. It must remain aligned with `drivers/media/usb/Makefile` so selectable drivers have build rules.

Risks and test signals: missing or wrongly guarded `source` lines hide drivers from configuration, while Makefile-only entries cannot be selected. Tests should run Kconfig parsing, menu visibility checks for each feature class, and build matrix checks for enabled USB camera/TV/DVB/SDR support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/usb/Makefile

Purpose: top-level build routing file for USB media drivers.

Important rules: unconditional `obj-y` descends into DVB USB-only support directories (`b2c2`, `dvb-usb`, `dvb-usb-v2`, `s2255`, `siano`, `ttusb-budget`, `ttusb-dec`). Conditional `obj-$(CONFIG_...)` entries build driver subdirectories such as `as102`, `airspy`, `gspca`, `hackrf`, `msi2500`, `pwc`, `uvc`, `au0828`, `cx231xx`, `em28xx`, `go7007`, `hdpvr`, `pvrusb2`, `stk1160`, and `usbtv`.

Control flow: kbuild evaluates the `obj-y` and config-conditioned object variables, descending into selected subdirectories. Comments require alphabetical ordering by directory/name.

State and persistence: no runtime state; build output depends on `.config`.

Dependencies and integration: must match symbols defined by sourced Kconfig files. The AirSpy line `obj-$(CONFIG_USB_AIRSPY) += airspy/` links the SDR driver selected in `usb/airspy/Kconfig`.

Risks and test signals: mismatched config symbols or missing subdirectory rules cause selected drivers not to build. Tests should run `make drivers/media/usb/` or targeted modules for selected configs, and check ordering/coverage against Kconfig sources when adding drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/airspy/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/usb/airspy/Kconfig

Purpose: Kconfig entry for the AirSpy USB software-defined-radio driver.

Important entry: `config USB_AIRSPY` is a tristate named "AirSpy", depends on `VIDEO_DEV`, and selects `VIDEOBUF2_VMALLOC`. Help text describes it as a V4L2 driver for AirSpy SDR devices and states the module name is `airspy`.

Control flow: this file is sourced only when USB SDR media support is enabled by the parent USB Kconfig. Selecting it as built-in or module controls `drivers/media/usb/airspy/Makefile`.

State and persistence: user choice persists in kernel configuration.

Dependencies and integration: depends on V4L2 core and videobuf2 vmalloc memory support. It is built by `obj-$(CONFIG_USB_AIRSPY) += airspy.o`.

Risks and test signals: missing `VIDEOBUF2_VMALLOC` selection would break buffer allocation support. Tests should cover Kconfig dependency resolution and module build with `CONFIG_USB_AIRSPY=m` and built-in where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/airspy/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/airspy/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/usb/airspy/Makefile

Purpose: kbuild rule for the AirSpy USB SDR driver object.

Important rule: `obj-$(CONFIG_USB_AIRSPY) += airspy.o` builds the AirSpy driver as built-in or module according to Kconfig.

Control flow: parent `drivers/media/usb/Makefile` descends into `airspy/` when `CONFIG_USB_AIRSPY` is enabled; this Makefile contributes `airspy.o` to the build.

State and persistence: no runtime state; build inclusion follows `.config`.

Dependencies and integration: must stay synchronized with `airspy/Kconfig` symbol and the source file name `airspy.c`.

Risks and test signals: symbol or object-name drift silently breaks the module build. Tests should build `CONFIG_USB_AIRSPY=m` and confirm the generated module is named `airspy`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/airspy/Makefile -->
