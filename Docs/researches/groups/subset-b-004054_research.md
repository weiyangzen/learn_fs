# subset-b-004054 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/au8522_dig.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/au8522_dig.c

Purpose: Implements the digital DVB frontend side of the Auvitek AU8522 hybrid demodulator. It exposes ATSC 8VSB and ITU J.83 Annex B QAM64/QAM256 support, programs modulation-specific AU8522 register tables, coordinates tuner programming through the frontend tuner ops, reports lock/statistics, and controls an optional status LED.

Important APIs/types/functions: `struct mse2snr_tab` and the `vsb_mse2snr_tab`, `qam64_mse2snr_tab`, and `qam256_mse2snr_tab` tables convert hardware MSE counters to SNR in dB * 10. `au8522_set_if()` writes IF-frequency registers for 3.25, 4, or 6 MHz IF choices from `struct au8522_config`. `au8522_enable_modulation()` applies the large VSB/QAM register tables and records `state->current_modulation`; QAM256 has a `zv_mode` alternate table and post-delay register clear for ZeeVee modulator compatibility. `au8522_set_frontend()` is the DVB core tune entry point, and `au8522_attach()` obtains shared AU8522 state, initializes the chip, installs `au8522_ops`, and leaves the I2C gate open for tuner access.

Control flow: Tuning first short-circuits when cached frequency and modulation already match. Otherwise the code opens the demod I2C gate, invokes tuner `set_params`, closes the gate, waits for tuner settling, and then writes the modulation table plus configured IF. Status reads inspect different demod registers for VSB (`0x0088`) versus QAM (`0x0541`), then derives signal/carrier either from demod lock or tuner lock according to `config.status_mode`. SNR and signal strength flow through the MSE lookup tables, with `au8522_led_status()` selecting LED off/weak/strong based on lock and per-modulation thresholds.

State and persistence: Runtime state is in shared `struct au8522_state`: `current_frequency`, `current_modulation`, `fe_status`, `led_state`, and `operational_mode`. There is no persistent storage; all hardware state is volatile AU8522 register programming plus module parameters `debug` and `zv_mode`.

Dependencies/integration: Depends on `au8522_priv.h` for state, register helpers, shared analog/digital lifetime, I2C gate control, and LED control. Integrates with DVB core through `dvb_frontend_ops`, with tuner drivers through `fe->ops.tuner_ops`, and with AU0828 USB bridge users via `au8522_attach()`.

Risks and test signals: Exercise VSB, QAM64, QAM256, and QAM256 `zv_mode` tuning paths; invalid modulation and IF rejection; tuner error propagation; lock reporting under both `AU8522_DEMODLOCKING` and `AU8522_TUNERLOCKING`; LED hysteresis around strong thresholds; SNR lookup edge cases where MSE is beyond the last threshold; and attach failure after shared state acquisition. The VSB SNR table contains a repeated/descending `43` entry before `53`, so table-order assumptions should be treated carefully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/au8522_dig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/au8522_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/au8522_priv.h

Purpose: Defines the private AU8522 hybrid-device contract shared by the digital demodulator and analog decoder files. It centralizes `struct au8522_state`, mode constants, pad indexes, shared helper prototypes, and the AU8522 register map/bit-value definitions used by both analog and digital programming sequences.

Important APIs/types/functions: `AU8522_ANALOG_MODE`, `AU8522_DIGITAL_MODE`, and `AU8522_SUSPEND_MODE` describe the active hardware function. `enum au8522_pads` describes media-controller pads when enabled. `struct au8522_state` owns the I2C client/adapter, shared tuner-I2C properties and hybrid instance list, board `struct au8522_config`, DVB frontend, cached digital tune state, LED state, V4L2 subdev/control state, analog input/std fields, and optional media pads. Shared routines include `au8522_writereg()`, `au8522_readreg()`, `au8522_init()`, `au8522_sleep()`, `au8522_get_state()`, `au8522_release_state()`, digital/analog I2C-gate control, and `au8522_led_ctrl()`.

Control flow: This header has no executable logic, but it defines the cross-file lifecycle. Attach paths call `au8522_get_state()` so analog and digital frontends can share one physical AU8522 instance, set `operational_mode`, then call common init/sleep and register helpers. Mode-specific code writes the register constants declared here to switch between ATSC/J83B, analog CVBS/S-video/RF, audio, GPIO, VBI, and transport-stream behavior.

State and persistence: State is entirely runtime kernel memory plus volatile AU8522 registers. The hybrid tuner instance list and `tuner_i2c_props` are the persistence-like mechanism within a boot session for sharing one I2C-addressed chip among multiple frontend/subdevice users.

Dependencies/integration: Includes Linux I2C, DVB frontend, V4L2 subdev/control/media-controller headers, `au8522.h` for public config, and `tuner-i2c.h` for hybrid sharing. Consumers include `au8522_dig.c` and the analog decoder implementation.

Risks and test signals: Validate analog/digital attach/release reference behavior, mode transitions, suspend/resume paths, I2C gate state across tuner calls, LED control availability, and media-controller pad setup. Because this header exposes a large raw register map, regressions are likely when symbolic values drift from data-sheet meanings or when a digital sequence accidentally reuses analog-only constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/au8522_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/bcm3510.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/bcm3510.c

Purpose: Implements the Broadcom BCM3510 ATSC/J.83B demodulator used by first-generation Air2PC hardware, including firmware download, Host Access Buffer command transport, built-in Panasonic CT10S tuner programming, acquisition setup, status/statistics, and DVB frontend registration.

Important APIs/types/functions: `struct bcm3510_state` owns the I2C adapter, board config, DVB frontend, `hab_mutex`, cached firmware/status timing, and cached HAB status responses. Low-level register access is `bcm3510_writebytes()`, `bcm3510_readbytes()`, `bcm3510_writeB()`, and `bcm3510_readB()`. HAB transport is `bcm3510_hab_send_request()`, `bcm3510_hab_get_response()`, and serialized `bcm3510_do_hab_cmd()`. Firmware and AP lifecycle are handled by `bcm3510_download_firmware()`, `bcm3510_reset()`, `bcm3510_clear_reset()`, `bcm3510_init_cold()`, and `bcm3510_init()`. Public entry is `bcm3510_attach()`.

Control flow: Attach allocates state, probes revision/layer at register `0xe0`, initializes the HAB mutex, resets the acquisition processor, and returns `bcm3510_ops`. Init checks JDEC state, downloads `dvb-fe-bcm3510-01.fw` when the AP waits at RAM, clears reset, optionally checks firmware version, and selects RF AGC. Tuning builds an acquire command for QAM256, QAM64, VSB8, or VSB16, disables/resets BERT counters, calculates tuner divider values from the requested frequency, sends a tuner command, clears cached status, and gives the AP time to acquire. Status/statistics read cached HAB status blocks and refresh them no more often than `status_check_interval`.

State and persistence: Firmware lives in device RAM and is reloaded when cold. Runtime state includes cached `status1/status2`, next refresh jiffies, and whether HAB commands are serialized by `hab_mutex`. No on-disk persistence exists; the external firmware blob is mandatory for cold start.

Dependencies/integration: Depends on `bcm3510.h` for platform firmware callback and demod I2C address, `bcm3510_priv.h` for packed register/command layouts, Linux firmware loading, DVB core, I2C, jiffies, and mutex APIs. Integration users include B2C2/flexcop Air2PC code.

Risks and test signals: Test firmware record parsing, revision probe for cold and warm signatures, reset/clear-reset timeouts, HAB timeout and mutex interruption, overlarge HAB buffers, AP already running, firmware version mismatch, status polling cadence changes after lock, tuner divider bounds, unsupported modulations, and BERT reset side effects. Several HAB command return values are ignored in refresh/tune paths, so I2C failure propagation and stale cached status deserve attention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/bcm3510.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/bcm3510.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/bcm3510.h

Purpose: Public board-driver interface for the BCM3510 demodulator. It declares the configuration structure, attach function, and Kconfig-disabled stub used by bridge drivers that instantiate the BCM3510 frontend.

Important APIs/types/functions: `struct bcm3510_config` supplies the demodulator I2C address and a board-provided `request_firmware()` callback taking the frontend, firmware pointer, and firmware name. `bcm3510_attach()` returns a `struct dvb_frontend *` when `CONFIG_DVB_BCM3510` is reachable; otherwise the inline stub logs a Kconfig warning and returns `NULL`.

Control flow: There is no runtime logic beyond the disabled-driver stub. Consumers create a static config, pass it with an I2C adapter to `dvb_attach(bcm3510_attach, ...)`, and then use the returned DVB frontend ops from `bcm3510.c`.

State and persistence: The header owns no state. It exposes the externally supplied firmware loading hook, which is the path by which the implementation obtains the persistent `dvb-fe-bcm3510-01.fw` firmware image.

Dependencies/integration: Includes DVB frontend and firmware headers. Used by B2C2/flexcop code for first-generation Air2PC ATSC boards.

Risks and test signals: Verify callers provide a valid firmware callback and demod address, handle `NULL` attach returns, and compile both built-in/module and Kconfig-disabled cases. Signature changes here affect every board file that attaches BCM3510.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/bcm3510.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/bcm3510_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/bcm3510_priv.h

Purpose: Defines private BCM3510 register bitfield layouts, HAB command IDs/message IDs, packed command/response structures, version constants, tuner command format, and logging helpers used by `bcm3510.c`.

Important APIs/types/functions: `bcm3510_register_value` is a union over one raw byte with named bitfield views for AP/HAB control/status, memory address/data, JDEC, revision, BER control, and tuner control registers. HAB structures include version info, external/internal tuner acquire, special symbol-rate/IF settings, auto reacquire, RF AGC selection, auto inversion, BERT control, tri-state, tuner control/data pairs, and status responses. Constants identify command groups such as `CMD_GET_VERSION_INFO`, `CMD_ACQUIRE`, `CMD_AUTO_PARAM`, `CMD_STATE_CONTROL`, `CMD_TUNE`, and `CMD_STATUS`.

Control flow: This header has no independent execution, but it defines the byte-level ABI for all `bcm3510_do_hab_cmd()` calls. `bcm3510.c` casts packed structures to byte buffers for HAB transmit/receive, and reads/writes `bcm3510_register_value` members before sending single-byte I2C register transactions.

State and persistence: Persistent-ish contract is the firmware/AP protocol: version constants `BCM3510_DEF_*` describe the expected firmware/script/config/demod versions. All structs are packed because they are sent directly over the Host Access Buffer and must match firmware layout.

Dependencies/integration: Consumed only by the BCM3510 implementation. It uses Linux integer types and relies on compiler bitfield layout for one-byte command/control fields.

Risks and test signals: Audit packed bitfield portability, command/message ID correctness, buffer sizes versus `MAX_XFER_SIZE`, and version checks. The mode constants are written with assignment syntax in `#define BCM3510_QAM16 = 0x01` style and are not used by the C file; using them later would be a compile hazard unless fixed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/bcm3510_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/bsbe1-d01a.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/bsbe1-d01a.h

Purpose: Provides static board-support data for the ALPS BSBE1-D01A satellite frontend variant using an STV0288 demodulator and STB6000 tuner.

Important APIs/types/functions: `stv0288_bsbe1_d01a_inittab` is a register/value initialization table terminated by `0xff, 0xff`. `stv0288_bsbe1_d01a_config` is a `struct stv0288_config` with demod address `0x68`, `min_delay_ms = 100`, and the initialization table pointer.

Control flow: The header has no functions. Board drivers include it and pass `&stv0288_bsbe1_d01a_config` to `stv0288_attach()`, after which the STV0288 driver consumes the inittab during demod initialization.

State and persistence: No mutable runtime state is owned here. The static table encodes volatile hardware reset/programming defaults for the demodulator.

Dependencies/integration: Includes `stb6000.h` and `stv0288.h`. Used by budget-ci style PCI DVB-S board setup for ALPS BSBE1-D01A hardware.

Risks and test signals: Validate that the inittab remains terminated, register pairs stay aligned, and the demod address/delay match the board wiring. Because this is a header with non-const static data, every including translation unit gets its own copy; changes should be limited to board-support contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/bsbe1-d01a.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/bsbe1.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/bsbe1.h

Purpose: Provides board-support data and tuner helper routines for the ALPS BSBE1 DVB-S frontend using an STV0299 demodulator and simple I2C PLL tuner.

Important APIs/types/functions: `alps_bsbe1_inittab` is the STV0299 initialization register table. `alps_bsbe1_set_symbol_rate()` selects ACLK/BCLK values from symbol-rate bands and writes ratio registers `0x1f` to `0x21`. `alps_bsbe1_tuner_set_params()` programs a four-byte tuner message at address `0x61` for 950 to 2150 MHz. `alps_bsbe1_config` fills `struct stv0299_config` with demod address `0x68`, `mclk = 88 MHz`, inversion, delay, and symbol-rate callback.

Control flow: Board drivers include this header, attach STV0299 with `alps_bsbe1_config`, and generally install `alps_bsbe1_tuner_set_params()` as the tuner callback. Tuning validates frequency, opens the frontend I2C gate if present, sends the PLL divider bytes, and leaves gate closure to surrounding frontend conventions.

State and persistence: No owned runtime state; the frequency divider bytes and STV0299 registers are volatile hardware state. `fe->tuner_priv` is expected to point to the I2C adapter.

Dependencies/integration: Requires STV0299 helper declarations and DVB/I2C types supplied by including board code. Used by TTPci budget/budget-ci board setup.

Risks and test signals: Test symbol-rate boundary bands, ratio byte programming, frequency limit rejection, I2C gate handling, and tuner I2C failure propagation. The tuner helper opens the gate but does not explicitly close it, so integration behavior depends on caller/demod conventions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/bsbe1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/bsru6.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/bsru6.h

Purpose: Provides static demod initialization and tuner programming helpers for ALPS BSRU6 DVB-S hardware using an STV0299 demodulator.

Important APIs/types/functions: `alps_bsru6_inittab` is the STV0299 register initialization table. `alps_bsru6_set_symbol_rate()` selects ACLK/BCLK values across symbol-rate ranges and writes the ratio registers. `alps_bsru6_tuner_set_params()` computes a rounded 125 kHz PLL divider, sends four bytes to tuner I2C address `0x61`, and switches a control byte for high-band frequencies above 1530 MHz. `alps_bsru6_config` sets demod address, clock, inversion, lock-output and voltage-output options, delay, and symbol-rate callback.

Control flow: Included board code passes `alps_bsru6_config` to `stv0299_attach()` and wires the tuner helper into frontend ops. Tune parameter flow validates satellite IF range, computes divider/control bytes, opens the demod I2C gate if present, and sends the tuner I2C transfer.

State and persistence: Header data is static initialization state only; no long-lived mutable state is owned. Register programming is volatile.

Dependencies/integration: Depends on STV0299 register helpers and DVB/I2C types from includers. Used by TTPci budget/budget-ci boards.

Risks and test signals: Validate table termination, symbol-rate thresholds, low/high-band control bytes, rounded divider math, frequency limits, and I2C transfer failure. As with `bsbe1.h`, I2C gate closure is not explicit in the helper and must be verified in board integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/bsru6.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx22700.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx22700.c

Purpose: Implements the Conexant CX22700 DVB-T OFDM demodulator frontend: I2C register access, initialization table programming, TPS setup/readback, lock/statistics reads, I2C gate control, and attach/export for bridge drivers.

Important APIs/types/functions: `struct cx22700_state` stores I2C adapter, config, and DVB frontend. `cx22700_writereg()`/`cx22700_readreg()` are low-level I2C accessors. `cx22700_set_inversion()`, `cx22700_set_tps()`, and `cx22700_get_tps()` translate DVB-T properties to/from chip registers. `cx22700_init()` soft-resets and writes `init_tab`. `cx22700_attach()` probes by reading register `0x07` and installs `cx22700_ops`.

Control flow: `set_frontend` soft-resets, invokes tuner `set_params`, closes the I2C gate if available, programs inversion/TPS, disables PAL loop filter, and restarts acquisition. Status derives signal from RS BER, carrier from TPS-valid bit, Viterbi/sync from status bit `0x10`, and lock from all lower status bits. BER and uncorrected block reads return counters and clear them by writing zero.

State and persistence: Runtime state is minimal and does not cache tune parameters. All demod state is volatile registers. No firmware or persistent storage is used.

Dependencies/integration: Public config comes from `cx22700.h`. Integrates with DVB core and bridge users such as TTUSB budget. Tuner programming is delegated to `fe->ops.tuner_ops`.

Risks and test signals: Test attach probe when read returns negative, invalid TPS fields, unsupported inversion auto, bandwidth selection, gate open/close, counter clear behavior, and lock bit interpretation. The bandwidth register code uses expressions like `cx22700_readreg(state, 0x09 | 0x10)` instead of ORing the returned value, which is suspicious and should be regression-tested before modifying.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx22700.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx22700.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx22700.h

Purpose: Public attach/configuration header for the CX22700 DVB-T demodulator.

Important APIs/types/functions: `struct cx22700_config` contains the demodulator I2C address. `cx22700_attach()` is declared when `CONFIG_DVB_CX22700` is reachable and replaced by a warning-returning inline stub otherwise.

Control flow: Board code creates a config, calls `dvb_attach(cx22700_attach, config, i2c)`, and handles a `NULL` return if the device is missing or disabled.

State and persistence: The header owns no state and exposes no firmware or persistent data.

Dependencies/integration: Includes Linux DVB frontend definitions and is consumed by USB/PCI bridge board setup files using the CX22700.

Risks and test signals: Compile-test reachable and disabled Kconfig cases, and verify all board callers pass the right demod address and handle attach failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx22700.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx22702.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx22702.c

Purpose: Implements the Conexant CX22702 DVB-T OFDM demodulator, including init, TPS auto/manual programming, serial/parallel transport output selection, lock/statistics, I2C gate control, and attach/export.

Important APIs/types/functions: `struct cx22702_state` stores I2C adapter, config, frontend, and previous uncorrected-block counter. `cx22702_writereg()`/`cx22702_readreg()` access chip registers. `cx22702_set_tps()` handles tuner programming, inversion, bandwidth, auto TPS mode, or manual modulation/FEC/hierarchy/guard/transmission registers. `cx22702_get_tps()` reads validated TPS values. `cx22702_init()` writes `init_tab` and output mode register `0xf8`. `cx22702_attach()` probes register `0x1f == 0x03`.

Control flow: Tuning first calls tuner `set_params`, then closes the I2C gate, programs inversion and bandwidth, forces LP FEC to auto due to a manual-mode limitation, and chooses automatic TPS if any property is auto. Manual mode writes explicit TPS fields and starts acquisition. Status reads demod status `0x0a` and AGC `0x23`; stats read BER/SNR from realtime or averaging registers and UCB deltas from a wrap-prone one-byte counter.

State and persistence: Only `prevUCBlocks` is cached in software. Demod configuration and counters live in volatile registers. No firmware is used.

Dependencies/integration: Public config is in `cx22702.h`; bridge users include cx88 and cxusb. Uses DVB core and standard I2C APIs.

Risks and test signals: Test output mode selection, invalid bandwidth/modulation/FEC/hierarchy/guard/transmission values, auto TPS acquisition, signal-strength scaling from register `0x23`, UCB delta wrap behavior, and attach probe. `cx22702_readreg()` returns `0` on I2C error, so failure can masquerade as valid register values in status/statistics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx22702.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx22702.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx22702.h

Purpose: Public board-driver interface for the CX22702 DVB-T demodulator.

Important APIs/types/functions: `struct cx22702_config` supplies demodulator I2C address and output mode. `CX22702_PARALLEL_OUTPUT` and `CX22702_SERIAL_OUTPUT` select transport output wiring. `cx22702_attach()` is declared or replaced by a Kconfig-disabled stub.

Control flow: Board drivers pass config and I2C adapter to `dvb_attach(cx22702_attach, ...)`; the implementation uses `output_mode` during init.

State and persistence: No state is owned by the header.

Dependencies/integration: Includes DVB frontend types and is consumed by cx88/cxusb board setup code.

Risks and test signals: Compile-test Kconfig variants, validate output-mode constants against board wiring, and ensure callers handle `NULL` attach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx22702.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx24110.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx24110.c

Purpose: Implements the Conexant CX24110 DVB-S demodulator frontend with CX24108-style tuner 3-wire writes, symbol-rate/FEC/inversion programming, DiSEqC and LNB voltage/tone control, statistics, and attach/export.

Important APIs/types/functions: `struct cx24110_state` stores I2C adapter/config/frontend and cached BER/BLER/EsN0 counters. `cx24110_regdata` is the initialization table. `cx24110_set_inversion()`, `cx24110_set_fec()`, `cx24110_get_fec()`, and `cx24110_set_symbolrate()` translate DVB-S properties to demod registers. `_cx24110_pll_write()` drives the tuner auto-mode 3-wire interface and is exposed via frontend `.write`; `cx24110_pll_write()` in the header formats 21-bit PLL words for that callback. SEC functions implement voltage, 22 kHz tone, DiSEqC master command, and burst.

Control flow: Attach probes chip ID register `0x00` for `0x5a` or `0x69`. Init writes the register table. Tuning delegates tuner params, programs inversion/FEC/symbol rate, and starts acquisition. Status combines frontend AGC and demod sync registers. BER/SNR/UCB reads update cached values only when corresponding hardware count-window-done bits are set, then return last cached data.

State and persistence: Cached counter fields avoid returning unstable in-progress hardware counts. All tune, SEC, and PLL state is volatile chip/register state; no firmware is loaded.

Dependencies/integration: Public interface in `cx24110.h`; board users include BT8xx PCTV Sat. Depends on DVB core, I2C, and SEC/DiSEqC APIs.

Risks and test signals: Test attach IDs, initialization table writes, auto/manual FEC, symbol-rate clamp and sample-clock selection, PLL busy waits, DiSEqC length validation, LNB voltage/tone register preservation, counter-window updates, and AFC frequency adjustment in `get_frontend()`. `_cx24110_pll_write()` contains unbounded busy waits on hardware bits, so hung hardware can stall callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx24110.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx24110.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx24110.h

Purpose: Public config/attach header for the CX24110 DVB-S demodulator and helper for writing tuner PLL words through the frontend `.write` callback.

Important APIs/types/functions: `struct cx24110_config` contains the demodulator I2C address. `cx24110_pll_write()` splits a 32-bit value into the top three bytes and invokes `fe->ops.write(fe, buf, 3)` when present. `cx24110_attach()` is declared or stubbed depending on `CONFIG_DVB_CX24110`.

Control flow: Board tuner code can call `cx24110_pll_write()` after attaching the demod; this reaches `_cx24110_pll_write()` in `cx24110.c`.

State and persistence: No state is stored here. The helper formats volatile tuner programming data.

Dependencies/integration: Includes DVB frontend types and is used by DVB-S bridge board code.

Risks and test signals: Validate that callers only use the PLL helper after attach, handle a missing `.write` callback, and tolerate Kconfig-disabled stubs. The helper silently returns success when `.write` is absent, which can hide board integration mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx24110.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx24113.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx24113.c

Purpose: Implements the Conexant CX24113/CX24128 satellite tuner as a DVB tuner subdevice, providing PLL calculation, bandwidth/gain programming, lock status, AGC callback support, and attach/export onto an existing demod frontend.

Important APIs/types/functions: `struct cx24113_state` stores I2C/config, revision/version, charge-pump/VCO/bandselect/gain/bandwidth configuration, frequency cache, reference divider, and fractional-window mode. Low-level access is `cx24113_writereg()`/`cx24113_readreg()`. Configuration helpers include `cx24113_set_parameters()`, `cx24113_set_gain_settings()`, `cx24113_set_Fref()`, `cx24113_enable()`, `cx24113_set_bandwidth()`, `cx24113_calc_pll_nf()`, `cx24113_set_nfr()`, and `cx24113_set_frequency()`. Public tuner ops are installed by `cx24113_attach()`, and `cx24113_agc_callback()` is exported for demod integration.

Control flow: Attach dummy-reads register 0, validates supported revisions `0x43` or `0x23`, records version, installs `cx24113_tuner_ops`, and stores state in `fe->tuner_priv`. Init seeds tuner defaults based on crystal frequency, writes parameter registers, sets initial gain/bandwidth/clock inversion, and adjusts crystal mode. Tuning derives bandwidth from symbol rate and rolloff, writes bandwidth, computes PLL integer/fractional divider with 64-bit math, writes N/F/R fields, toggles VCO divider/bandselect bits, and checks PLL lock. The AGC callback repeatedly reads demod signal strength and updates tuner gain until stable.

State and persistence: Runtime state caches all computed tuner-control parameters and the last requested frequency. Hardware state is volatile I2C registers; no firmware or persistent storage exists.

Dependencies/integration: Public config in `cx24113.h`; used with demods such as CX24123 via B2C2/flexcop. Depends on DVB tuner ops and `do_div()`-style 64-bit division.

Risks and test signals: Test revision-specific VCO/ref-divider handling, crystal-frequency branches, PLL calculation boundaries where `N < 6`, fractional-window clamping, bandwidth calculations for low/high symbol rates, gain-threshold hysteresis, lock reporting, and attach cleanup. `cx24113_agc_callback()` assumes the paired demod's signal-strength scale and casts a `u16 *` to signed data, so cross-demod reuse is risky.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx24113.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx24113.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx24113.h

Purpose: Public interface for attaching the CX24113/CX24128 satellite tuner to an existing DVB frontend.

Important APIs/types/functions: `struct cx24113_config` supplies tuner I2C address (`0x14` or `0x54`) and crystal frequency in kHz. `cx24113_attach()` installs tuner ops on an existing frontend. `cx24113_agc_callback()` is exported so paired demod drivers can trigger tuner gain adjustment. Disabled-Kconfig inline stubs warn and return `NULL`/no-op.

Control flow: Board code calls `dvb_attach(cx24113_attach, fe, config, i2c)` after creating the demod frontend, then optionally wires AGC callback usage through the paired demod.

State and persistence: No state in the header; runtime tuner state is allocated in `cx24113.c`.

Dependencies/integration: Forward-declares `struct dvb_frontend`; callers must include I2C definitions. Used in B2C2/flexcop satellite frontend setup.

Risks and test signals: Verify I2C address and `xtal_khz` correctness, Kconfig-disabled build paths, caller handling of `NULL`, and compatibility of AGC callback assumptions with the selected demod.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx24113.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx24116.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx24116.c

Purpose: Implements the Conexant CX24116/CX24118 DVB-S/DVB-S2 satellite demod/tuner frontend. It loads firmware on demand, sends mailbox commands, maps DVB-S/S2 modulation/FEC/pilot/rolloff into firmware tune requests, manages LNB voltage/tone/DiSEqC, and reports lock/statistics.

Important APIs/types/functions: `struct cx24116_state` stores I2C/config/frontend, current/next `struct cx24116_tuning`, firmware recursion guard, cached DiSEqC burst, and cached DiSEqC command. `CX24116_MODFEC_MODES` maps delivery system, modulation, and FEC to firmware mask/value bytes. `cx24116_firmware_ondemand()`, `cx24116_load_firmware()`, and `cx24116_cmd_execute()` own firmware upload and command execution. `cx24116_set_frontend()` validates properties and builds `CMD_TUNEREQUEST`. SEC helpers implement LNB config, DC level, tone, DiSEqC message, and burst behavior.

Control flow: Attach probes chip ID `0x0501`. Init powers clocks, executes tuner sleep-off command, initializes DiSEqC, and sets 13V default voltage. Firmware is loaded when reset register indicates it is needed; upload resets the device, initializes PLL, writes the firmware in chunks honoring `config->i2c_wr_max`, then runs VCO, tuner, MPEG, and firmware-version commands. Tuning validates DVB-S versus DVB-S2 constraints, sets inversion/FEC/symbol rate, optionally calls board `set_ts_params`, resets bandwidth, constructs tune bytes, adjusts clock/rate dividers for high symbol rates, and retries pilot when `PILOT_AUTO` is emulated. `tune()` returns hardware-algorithm polling behavior to DVB core.

State and persistence: Firmware state persists only in device RAM. The driver caches current/next tuning because firmware cannot easily report all parameters. DiSEqC message/burst may be cached depending on `toneburst` module parameter. Module parameters `debug`, `toneburst`, and `esno_snr` alter diagnostics and behavior.

Dependencies/integration: Public config in `cx24116.h` supplies I2C write limit plus optional board reset, MPEG/TS callbacks. Uses Linux firmware loader, DVB core, I2C, and SEC/DiSEqC APIs. Bridge users include cx23885, cx88, dm1105, anysee, dw2102, and related boards.

Risks and test signals: Test missing firmware, reset callback, chunked and unchunked firmware writes, command timeout, recursive firmware guard, all modulation/FEC tables, DVB-S2 unsupported auto FEC, pilot retry, rolloff validation, high-symbol-rate divider branch, LNB wait timeout, toneburst modes, DiSEqC length, SNR unit module parameter, sleep/wake, and board callbacks. `cx24116_cmd_execute()` reuses `i` after the command-write loop for timeout counting, so timeout duration depends on command length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx24116.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx24116.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx24116.h

Purpose: Public board-driver config/attach header for the CX24116/CX24118 DVB-S/S2 frontend.

Important APIs/types/functions: `struct cx24116_config` provides demod I2C address, optional `set_ts_params()` callback for DMA/TS setup, optional `reset_device()` callback used during firmware loading, MPEG clock polarity field `mpg_clk_pos_pol`, and maximum I2C write size `i2c_wr_max`. `cx24116_attach()` is declared or Kconfig-stubbed.

Control flow: Bridge drivers pass board-specific callbacks and limits into attach. The implementation consumes them during firmware loading, MPEG setup, and tune preparation.

State and persistence: No header-owned state. The firmware file name is private to the C file, but this config controls how firmware upload is physically performed.

Dependencies/integration: Includes DVB frontend types and is consumed by multiple PCI/USB satellite bridge drivers.

Risks and test signals: Verify each board provides correct reset and TS callbacks, handles `NULL` attach, and sets `i2c_wr_max` to match adapter transfer limits. The bitfield width declaration for `mpg_clk_pos_pol` is unusual (`:0x02`) but equivalent to width 2; changes should preserve ABI expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx24116.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx24117.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx24117.c

Purpose: Implements the dual-demod Conexant CX24117/CX24132 DVB-S/DVB-S2 frontend. It shares one physical I2C/firmware device between two DVB frontends, serializes firmware commands, handles firmware upload, tunes each demod independently, controls LNB/DiSEqC GPIOs, and reports per-demod statistics.

Important APIs/types/functions: `struct cx24117_priv` is the shared state: demod address, I2C adapter, firmware recursion guard, command mutex, and hybrid tuner list node. `struct cx24117_state` is per-frontend state: shared priv, frontend, current/next tuning, DiSEqC command, and demod index. `cx24117_get_priv()`/`cx24117_release_priv()` use `hybrid_tuner_request_state()` to share state across two attaches. `cx24117_cmd_execute()` wraps `cx24117_cmd_execute_nolock()` with `priv->fe_lock`. Firmware, tuning, SEC, and stat functions mirror CX24116 but include demod index fields and per-demod register banks.

Control flow: Attach obtains or creates shared priv, assigns demod index `0` or `1`, and returns one frontend without immediate chip probe. Firmware is loaded on first command if register `0xeb` is not `0x0a`; upload writes setup registers, sends the entire firmware via one I2C message to register `0xfa`, then runs demod init, VCO, tuner init, global/per-demod MPEG config, and firmware-version commands. Init wakes the selected demod, initializes DiSEqC, BER control, RS correction, and GPIO direction under the shared lock. Tuning validates DVB-S/S2 properties, supports rolloff-auto by retrying 0.35/0.25/0.20, chooses divider registers by symbol-rate band, sends `CMD_TUNEREQUEST`, and polls for signal+sync.

State and persistence: Shared firmware and command state persist while any frontend references the shared priv. Per-demod tuning caches feed `get_frontend()` and retry behavior. Hardware state is volatile; firmware is `dvb-fe-cx24117.fw` in device RAM.

Dependencies/integration: Public config in `cx24117.h`, Linux firmware loader, DVB core, SEC APIs, `tuner-i2c.h` hybrid-state helpers, and bridge users such as cx23885 TBS dual tuner cards.

Risks and test signals: Test dual attach/release reference counts, concurrent commands from both demods, firmware upload failure cleanup, missing firmware, init on each demod, GPIO LNB power polarity, rolloff-auto retries, per-demod register-bank selection, status/stat reads, get_frontend mapping, DiSEqC waits, and sleep/wake. `cx24117_read_ber()` assembles the four-byte BER value using `buf[1]` and `buf[0]` twice instead of all four bytes, which looks like a real statistics bug worth targeted verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx24117.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx24117.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx24117.h

Purpose: Public attach/config header for the CX24117/CX24132 dual DVB-S/S2 demodulator.

Important APIs/types/functions: `struct cx24117_config` contains the shared demodulator I2C address. `cx24117_attach()` returns one `struct dvb_frontend *` per call and internally assigns demod 0/1 through shared state. Disabled-Kconfig stub warns via `dev_warn(&i2c->dev, ...)` and returns `NULL`.

Control flow: Board drivers call attach once for each frontend on a dual-demod device, using the same I2C adapter/address. The C implementation uses the repeated attach calls to allocate or reuse shared private state.

State and persistence: No header-owned state. The simple config intentionally exposes only the shared I2C address; all dual-demod sharing lives in `cx24117.c`.

Dependencies/integration: Includes DVB frontend types and is used by cx23885 board setup for TBS6980/TBS6981-style cards.

Risks and test signals: Verify board code calls attach the right number of times, handles partial second-frontend failure, and uses the same address/adapter for both frontends. Kconfig-disabled builds require a valid `i2c` pointer because the stub logs through `i2c->dev`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cx24117.h -->
