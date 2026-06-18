# subset-b-004069 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dvb-pll.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dvb-pll.c

### Purpose
`dvb-pll.c` is the shared simple PLL tuner implementation for legacy DVB frontends. It provides descriptor-driven programming for many Thomson, LG, Infineon, Philips, Alps, Samsung, Panasonic, Opera, Friio, and EarthSoft tuner variants, then exposes them through `dvb_tuner_ops` and an optional I2C driver binding.

### Important APIs, Types, And Functions
`struct dvb_pll_desc` describes each tuner: name, frequency range, IF offset, optional init/sleep data, optional `set()` adjustment hook, and limit/step/config/cb table entries. `struct dvb_pll_priv` stores the chosen descriptor, I2C adapter/address, an IDA slot, and cached tuned frequency/bandwidth. `dvb_pll_attach()` is the legacy exported attach API. `dvb_pll_configure()` computes the PLL divisor and four-byte payload. Tuner callbacks include `dvb_pll_init()`, `dvb_pll_sleep()`, `dvb_pll_set_params()`, `dvb_pll_calc_regs()`, and frequency/bandwidth getters.

### Control Flow
Attach allocates a temporary probe byte and IDA number, optionally overrides the requested descriptor through the debug `id[]` module parameter, probes the I2C address when an adapter is provided, allocates private state, installs tuner ops, fills tuner info, and suppresses init/sleep callbacks when no descriptor data exists. Set-params selects the first descriptor entry whose limit covers the requested frequency, computes `(frequency + iffreq + stepsize / 2) / stepsize`, lets descriptor-specific hooks adjust bandwidth or special writes, sends the four bytes over I2C through an opened frontend gate, and caches the actual programmed frequency.

### State, Persistence, And Dependencies
Persistent driver state is in `fe->tuner_priv`; the IDA slot tracks debug override slots and is freed by the I2C remove path, but the legacy release path only frees private data. Hardware state persists in tuner registers written over I2C. Dependencies include `dvb_frontend`, `i2c_transfer`, optional `fe->ops.i2c_gate_ctrl`, IDA, module parameters, and Kconfig reachability through `dvb-pll.h`.

### Integration Points
Boards can call `dvb_pll_attach()` directly or instantiate the `dvb_pll` I2C driver with `struct dvb_pll_config` platform data. The attach path populates `fe->ops.tuner_ops`, while the I2C probe clears `tuner_ops.release` to avoid double module release when `dvb_module_release()` also owns lifetime.

### Risks
`BUG_ON()` rejects invalid descriptor IDs and can crash if callers pass bad IDs. Legacy attach does not free the IDA slot in `dvb_pll_release()`, while I2C remove does. Descriptor tables encode many hardware-specific magic values and several hooks perform immediate I2C writes before final buffer edits. I2C gate close is inconsistent after some writes. The debug `id[]` override can force incompatible descriptors.

### Test Signals
Useful tests are attach/probe failure paths, per-descriptor frequency boundary tuning, 6/7/8 MHz bandwidth-specific hooks, init/sleep data writes, `calc_regs()` buffer sizing, no-I2C attach behavior, I2C-driver remove lifetime, and forced `id[]` descriptor overrides.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dvb-pll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dvb-pll.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dvb-pll.h

### Purpose
`dvb-pll.h` declares the public interface and descriptor IDs for the simple DVB PLL tuner helper implemented in `dvb-pll.c`.

### Important APIs, Types, And Functions
The header defines numeric `DVB_PLL_*` IDs from `DVB_PLL_UNDEFINED` through `DVB_PLL_TDA665X_EARTH_PT1`. `struct dvb_pll_config` carries the frontend pointer used by the I2C-client probe path. `dvb_pll_attach()` attaches a descriptor-selected PLL to a frontend, I2C address, and adapter.

### Control Flow
There is no runtime logic beyond Kconfig reachability. When `CONFIG_DVB_PLL` is reachable, callers link to the exported attach function. Otherwise the inline stub logs a warning and returns `NULL`.

### State, Persistence, And Dependencies
The header stores no state. It depends on Linux I2C and DVB frontend declarations and must stay synchronized with the descriptor array and I2C device table in `dvb-pll.c`.

### Integration Points
Board drivers use the constants to choose a tuner descriptor. I2C module loading uses `struct dvb_pll_config` as platform data for the I2C driver probe.

### Risks
The numeric ID ABI is order-sensitive: changing values without updating board users breaks descriptor selection. The stub returns `NULL`, so callers must handle disabled Kconfig builds.

### Test Signals
Build tests should cover reachable and disabled Kconfig cases, all descriptor IDs used by board files, and I2C-platform-data attach paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dvb-pll.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dvb_dummy_fe.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dvb_dummy_fe.c

### Purpose
`dvb_dummy_fe.c` implements synthetic DVB-T, DVB-C, and DVB-S frontend instances for bridge drivers or test configurations that need a frontend object without real demodulator hardware.

### Important APIs, Types, And Functions
`struct dvb_dummy_fe_state` only embeds a `dvb_frontend`. The exported attach functions are `dvb_dummy_fe_ofdm_attach()`, `dvb_dummy_fe_qpsk_attach()`, and `dvb_dummy_fe_qam_attach()`. Shared callbacks report a permanent lock, zero BER/SNR/strength/uncorrected blocks, no-op init/sleep/tone/voltage, and a set-frontend path that delegates tuner programming when present.

### Control Flow
Each attach function allocates state, copies a static `dvb_frontend_ops` template for OFDM, QPSK, or QAM, sets `demodulator_priv`, and returns the embedded frontend. `set_frontend()` calls `fe->ops.tuner_ops.set_params()` if installed and then closes the I2C gate when available. `read_status()` always sets all lock bits.

### State, Persistence, And Dependencies
State is memory-only and has no hardware persistence. The frontend operation templates encode delivery systems, ranges, symbol-rate limits, and capability flags. The module depends on DVB core structures and any attached tuner operations supplied by a parent driver.

### Integration Points
The module exports all three attach symbols for users needing dummy frontend registration. DVB-S dummy instances also provide SEC tone and voltage callbacks so satellite control calls do not fail.

### Risks
Because lock and quality metrics are fabricated, this driver can mask tuner, transport, or bridge failures if used outside intended dummy/test contexts. `get_frontend()` returns success without populating properties, and set-frontend ignores tuner errors.

### Test Signals
Test with frontend registration/unregistration, each delivery-system ops table, tuner delegation with I2C gate close, disabled Kconfig stubs, and userspace scans that expect permanent lock with zero metrics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dvb_dummy_fe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dvb_dummy_fe.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dvb_dummy_fe.h

### Purpose
`dvb_dummy_fe.h` exposes the attach API for dummy OFDM, QPSK, and QAM DVB frontends.

### Important APIs, Types, And Functions
It declares `dvb_dummy_fe_ofdm_attach()`, `dvb_dummy_fe_qpsk_attach()`, and `dvb_dummy_fe_qam_attach()` when `CONFIG_DVB_DUMMY_FE` is reachable, with inline warning stubs otherwise.

### Control Flow
The header has only Kconfig dispatch. Enabled builds use exported module functions; disabled builds warn and return `NULL`.

### State, Persistence, And Dependencies
No state is stored here. It depends on Linux DVB frontend headers and `pr_warn()` availability from included kernel headers.

### Integration Points
Bridge or board drivers include this header to create dummy frontend objects while keeping compile-time optionality.

### Risks
Callers must treat `NULL` as a valid disabled-module result. The header exposes no configuration knobs, so behavior is fully determined by `dvb_dummy_fe.c`.

### Test Signals
Build both reachable and disabled Kconfig variants and verify callers properly handle `NULL` attach returns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/dvb_dummy_fe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ec100.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ec100.c

### Purpose
`ec100.c` is an E3C EC100 DVB-T demodulator driver. It handles single-byte register I2C access, tuning-time demodulator setup, status and metric reads, and frontend attachment.

### Important APIs, Types, And Functions
`struct ec100_state` stores the I2C adapter, copied `ec100_config`, embedded frontend, and previous 16-bit BER counter. `ec100_attach()` is exported. Internal helpers are `ec100_write_reg()`, `ec100_read_reg()`, `ec100_set_frontend()`, `ec100_read_status()`, BER/strength/SNR/ucblocks readers, and `ec100_get_tune_settings()`.

### Control Flow
Attach allocates state, copies the config, reads register `0x33`, and requires chip ID `0x0b`. Tuning first calls an attached tuner, then writes a fixed sequence of EC100 registers, selecting bandwidth-dependent values for registers `0x1b` and `0x1c`, programs IF registers, and toggles register `0x00` to start acquisition. Status reads register `0x42` for full lock or falls back to register `0x01` for partial signal/carrier/viterbi indications.

### State, Persistence, And Dependencies
The only cached runtime metric is previous BER, used to report deltas from the hardware counter. All other state is hardware register state. Dependencies are DVB frontend property cache, I2C transfers, optional tuner ops, and the config header for demodulator address.

### Integration Points
`ec100_ops` exposes a DVB-T demodulator with tuner delegation via `fe->ops.tuner_ops`. Parent board drivers attach a tuner separately and then register this demodulator frontend.

### Risks
Register programming is hard-coded and only bandwidth selection varies. Tuner `set_params()` return is ignored. SNR and uncorrected blocks are always zero. BER counter wrap handling is minimal and may under-report on multiple wraps. Errors are logged with I2C adapter device context.

### Test Signals
Test chip ID probing, I2C error propagation, 6/7/8 MHz tuning values, lock and partial-lock status bits, BER delta/wrap behavior, tuner delegation, and frontend release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ec100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ec100.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ec100.h

### Purpose
`ec100.h` declares the configuration and attach entry point for the EC100 DVB-T demodulator.

### Important APIs, Types, And Functions
`struct ec100_config` contains the demodulator I2C address. `ec100_attach()` returns a `dvb_frontend *` for a given config and I2C adapter when `CONFIG_DVB_EC100` is reachable.

### Control Flow
Enabled builds link to the real attach function. Disabled builds use an inline stub that logs a warning and returns `NULL`.

### State, Persistence, And Dependencies
No state is stored in the header. It depends on DVB frontend and I2C adapter declarations.

### Integration Points
Board drivers supply the I2C demod address through `ec100_config` and then attach a tuner through the returned frontend's tuner ops.

### Risks
Only the address is configurable, so board-specific IF or GPIO sequencing must be handled elsewhere. Disabled Kconfig stubs require caller-side `NULL` handling.

### Test Signals
Build tests for enabled/disabled Kconfig and board attach paths with the configured demodulator address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ec100.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/eds1547.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/eds1547.h

### Purpose
`eds1547.h` provides static support data for an Earda EDS-1547 tuner/NIM using the STV0288 demodulator.

### Important APIs, Types, And Functions
The file defines `stv0288_earda_inittab[]`, a register/value initialization table terminated by `0xff, 0xff`, and `earda_config`, a `struct stv0288_config` with demod address `0x68`, `min_delay_ms = 100`, and the init table pointer.

### Control Flow
There is no executable control flow in the header. Consumers include it to get a ready-made STV0288 config and initialization table.

### State, Persistence, And Dependencies
The table is static data compiled into including translation units. Hardware persistence occurs when a caller's STV0288 driver writes the table to the demodulator. The header depends on a visible `struct stv0288_config` definition from the includer.

### Integration Points
This is a board-support include used by DVB USB or satellite board code that wires an EDS-1547 frontend to the STV0288 demodulator driver.

### Risks
Defining non-const `static` objects in a header duplicates data in every includer. The header assumes the includer already included STV0288 declarations. Any register table mistake is hardware-specific and hard to validate without the NIM.

### Test Signals
Compile the including board file, verify the STV0288 init table is accepted, check lock after init on EDS-1547 hardware, and confirm the terminator prevents overrun.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/eds1547.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/gp8psk-fe.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/gp8psk-fe.c

### Purpose
`gp8psk-fe.c` implements the frontend layer for Genpix USB DVB-S/Turbo-FEC/8PSK receivers. It translates DVB frontend operations into device-specific USB control operations supplied by a parent driver.

### Important APIs, Types, And Functions
`struct gp8psk_fe_state` stores the embedded frontend, parent private pointer, command ops, revision flag, cached lock/SNR, and status polling interval. `gp8psk_fe_attach()` is exported and requires `in`, `out`, and `reload` callbacks. Key callbacks include `gp8psk_fe_set_frontend()`, `gp8psk_fe_read_status()`, `gp8psk_fe_read_snr()`, signal strength mapping, DiSEqC/tone/voltage control, high LNB voltage, and legacy Dish Network command support.

### Control Flow
Set-frontend packs symbol rate and frequency into a 10-byte command buffer, normalizes DVB-S plus PSK_8 into `SYS_TURBO`, validates modulation and delivery system, maps FEC values to firmware fields, optionally reloads revision-1 firmware when leaving DCII mode, sends `TUNE_8PSK`, and resets cached status polling. Status reads are rate-limited with `jiffies`; unlocked state polls every 100 ms and locked state every 1000 ms.

### State, Persistence, And Dependencies
Driver state is memory-only; device state is controlled by parent `gp8psk_fe_ops` commands. Cached `lock` and `snr` reduce USB traffic. It depends on Genpix command constants from the header, DVB frontend cache fields, module debug parameter, and parent USB transport.

### Integration Points
The parent USB driver supplies command callbacks and receives all hardware I/O. The frontend advertises DVB-S caps with Turbo-FEC compatibility and provides satellite SEC controls.

### Risks
Many `ops->in/out` return values are ignored, especially status polling and tune command completion. DiSEqC burst comments admit likely-wrong commands. `set_voltage()` maps any non-18V value to false, including OFF and invalid enum values. DVB-S2 is accepted only for backward compatibility without distinct command mapping.

### Test Signals
Test revision-1 reload paths, QPSK/8PSK/16QAM FEC mapping, unsupported modulation errors, status polling cadence, SNR-to-strength scaling, DiSEqC/tone/voltage USB commands, and parent callback failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/gp8psk-fe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/gp8psk-fe.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/gp8psk-fe.h

### Purpose
`gp8psk-fe.h` defines the Genpix command protocol constants, firmware revision helpers, parent operation callbacks, and frontend attach entry point.

### Important APIs, Types, And Functions
The header enumerates USB request IDs such as `TUNE_8PSK`, `GET_SIGNAL_LOCK`, `SET_LNB_VOLTAGE`, and `SEND_DISEQC_COMMAND`; configuration bit masks like `bmDCtuned`; advanced modulation IDs; `GP8PSK_FW_VERS()`; `struct gp8psk_fe_ops`; and `gp8psk_fe_attach()`.

### Control Flow
No executable control flow exists. The implementation uses these constants to form parent USB control transfers.

### State, Persistence, And Dependencies
No state is stored in the header. It depends on Linux integer types and a visible `bool` type in includers.

### Integration Points
USB bridge code includes this header to issue firmware commands and attach the demodulator frontend with transport callbacks.

### Risks
The command constants are a hardware/firmware ABI. Mismatched firmware revisions, wrong request directions, or incorrect modulation IDs directly break tuning and SEC control.

### Test Signals
Compile parent users, verify firmware version decoding, and test each command ID against known Genpix firmware revisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/gp8psk-fe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/helene.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/helene.c

### Purpose
`helene.c` is the Sony HELENE CXD2858ER tuner driver for satellite, terrestrial, cable, and ISDB systems. It programs tuner analog, PLL, AGC, IF/IQ output, and power-save registers based on frontend delivery system and bandwidth.

### Important APIs, Types, And Functions
`struct helene_priv` stores I2C address/adapter, active frequency in kHz, state, parent tuner-selection callback, and crystal enum. The file defines Sony TV-system enums, a terrestrial adjustment table, register I/O helpers, power-save helpers, `helene_get_tv_system()`, satellite and terrestrial tuning paths (`helene_set_params_s()` and `_t()`), shared `helene_set_params()`, and `helene_x_pon()` power-on initialization. Public entry points are `helene_attach()`, `helene_attach_s()`, and the I2C-driver `helene_probe()`.

### Control Flow
Attach allocates private state, opens the demod I2C gate, runs `helene_x_pon()`, closes the gate, installs tuner ops, and stores `fe->tuner_priv`. `helene_x_pon()` performs a large first-power-on sequence, boots the internal CPU, checks CPU status, calibrates VCO current, disables outputs, and enters standby. Tuning maps DVB/ISDB/cable/satellite properties to a Sony TV-system ID, switches board RF path through the optional callback, wakes power-save as needed, computes rounded frequency, selects table-driven gain/overload/filter offsets for terrestrial modes or symbol-rate-based LPF for satellite modes, then writes burst register blocks.

### State, Persistence, And Dependencies
State persists in `fe->tuner_priv` or devm-managed I2C-client data. `priv->state` prevents redundant power-save transitions, and `priv->frequency` backs `get_frequency()`. Hardware register settings persist until sleep or retune. Dependencies include I2C transfer APIs, optional frontend I2C gate control, parent RF-switch callback, DVB frontend property cache, and HELENE config values.

### Integration Points
Legacy board drivers can attach terrestrial-only or satellite-only tuner ops, while I2C-device users get combined Sat/Ter ops. The parent callback selects which RF path is active, making this driver part of multi-standard frontend stacks.

### Risks
Most register writes ignore return values, so partial I2C failures can still report success. `helene_probe()` uses devm allocation but installs a normal `release` callback that calls `kfree()` on `fe->tuner_priv`, creating a lifetime mismatch if the frontend releases devm memory. The terrestrial table is indexed by enum values and must remain aligned. Frequency units differ internally between satellite, terrestrial, and `get_frequency()`.

### Test Signals
Test legacy and I2C-client attach, CPU error handling in `helene_x_pon()`, all supported delivery-system/bandwidth mappings, RF-switch callback behavior, sleep/init transitions, I2C gate open/close, devm lifetime release, and tuned-frequency reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/helene.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/helene.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/helene.h

### Purpose
`helene.h` exposes configuration and attach APIs for the Sony HELENE tuner driver.

### Important APIs, Types, And Functions
`enum helene_xtal` lists supported crystal frequencies. `struct helene_config` carries I2C address, legacy MHz crystal value, RF-switch callback context/function, crystal enum, and a frontend pointer for I2C-client platform data. `helene_attach()` attaches terrestrial/cable ops, and `helene_attach_s()` attaches satellite ops.

### Control Flow
Enabled builds link to real attach functions. Disabled builds provide warning stubs returning `NULL`.

### State, Persistence, And Dependencies
The header stores no state. It depends on Linux DVB frontend and I2C declarations. Runtime state is allocated by `helene.c` based on this config.

### Integration Points
Board drivers and I2C platform-data users configure tuner address, crystal selection, and RF-switch callback through this header.

### Risks
The documentation for `helene_config` includes both `xtal_freq_mhz` and `xtal`, but the implementation primarily uses `xtal`. Callers must provide a valid frontend in I2C-client platform data.

### Test Signals
Build with enabled/disabled Kconfig, attach both terrestrial and satellite variants, and validate every supported `helene_xtal` value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/helene.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/horus3a.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/horus3a.c

### Purpose
`horus3a.c` implements a Sony HORUS3A DVB-S/S2 satellite tuner. It programs PLL divider, gain, LPF cutoff, calibration, IQ generator, and power-save state over I2C.

### Important APIs, Types, And Functions
`struct horus3a_priv` stores frequency, I2C address/adapter, sleep/active state, and an optional parent RF-selection callback. Helpers include bounded register writes, power-save enter/leave, `horus3a_set_params()`, frequency getter, and `horus3a_attach()`.

### Control Flow
Attach allocates state, normalizes the 8-bit address by shifting right, opens the demod I2C gate, waits after power-on, disables IQ generation, programs reference divider from `xtal_freq_mhz`, selects oscillator tuning value for 27/24/16 MHz crystals, enters power save, closes the gate, and installs tuner ops. Tuning calls the parent callback, leaves power save, rounds frequency to MHz, computes mixer divider and PLL `ms`, chooses F/G control bands from frequency ranges, computes LPF cutoff from DVB-S or DVB-S2 symbol rate formulas, writes registers `0x00` through `0x04`, gain/filter registers, starts calibration, enables IQ generation, waits 60 ms, and caches actual frequency.

### State, Persistence, And Dependencies
State lives in `fe->tuner_priv`; hardware state persists in tuner registers. `priv->state` avoids duplicate power-save writes. Dependencies include I2C transfer, sleep delays, optional I2C gate control, parent tuner callback, and DVB property cache delivery system/symbol rate/frequency.

### Integration Points
The driver fills `fe->ops.tuner_ops` for a satellite demodulator. Parent hardware can switch active tuner paths using `set_tuner_callback`.

### Risks
Most register write results are ignored, so retune may report success after I2C failure. Invalid crystal values only warn and continue with zeroed tuning value. The attach function does not verify chip identity. Delivery systems other than DVB-S/S2 return `-EINVAL`.

### Test Signals
Test attach with 16/24/27 MHz crystals, power-save transitions, DVB-S and DVB-S2 LPF calculations, boundary frequencies for gain/mixer ranges, parent callback behavior, I2C gate sequencing, and I2C error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/horus3a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/horus3a.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/horus3a.h

### Purpose
`horus3a.h` declares configuration and attach API for the Sony HORUS3A satellite tuner.

### Important APIs, Types, And Functions
`struct horus3a_config` contains the tuner I2C address, oscillator frequency in MHz, and optional parent callback context/function. `horus3a_attach()` attaches tuner ops to an existing frontend.

### Control Flow
Enabled Kconfig builds use the exported attach function. Disabled builds warn and return `NULL`.

### State, Persistence, And Dependencies
No state is stored in the header. Runtime state is allocated by `horus3a.c`. It depends on Linux DVB frontend and I2C types.

### Integration Points
Satellite board drivers pass this config when wiring HORUS3A behind a demodulator-controlled I2C gate.

### Risks
The attach comment incorrectly refers to `struct helene_config`, which can mislead users. Callers must use the address format expected by the implementation, which shifts `i2c_address` right by one.

### Test Signals
Build enabled/disabled Kconfig variants, attach with board configs, and validate callback invocation plus address handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/horus3a.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/isl6405.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/isl6405.c

### Purpose
`isl6405.c` is an SEC/LNB power controller driver for the dual-output Intersil ISL6405. It overrides frontend voltage and high-LNB-voltage operations by writing the ISL6405 control register over I2C.

### Important APIs, Types, And Functions
`struct isl6405` stores the mutable config byte, force-set/force-clear masks, I2C adapter/address, and no embedded frontend. `isl6405_attach()` is exported. Callback functions are `isl6405_set_voltage()`, `isl6405_enable_high_lnb_voltage()`, and `isl6405_release()`.

### Control Flow
Attach allocates state, selects default current-limit bit for output 1 or output 2 based on the `0x80` selector in `override_set`, stores override masks, assigns `fe->sec_priv`, and detects the chip by writing voltage off. Voltage setting clears output-specific enable/voltage bits, maps OFF/13V/18V to register bits, reapplies override masks, and writes one byte. High-voltage mode toggles LLC bits for the selected output. Release powers off and frees `sec_priv`.

### State, Persistence, And Dependencies
The config byte is cached in memory and mirrored to hardware on each operation. Dependencies include DVB SEC voltage enums, I2C transfer, and bit definitions from `isl6405.h`.

### Integration Points
The driver installs `fe->ops.release_sec`, `fe->ops.set_voltage`, and `fe->ops.enable_high_lnb_voltage`, allowing it to coexist with a demodulator frontend while owning SEC power behavior through `fe->sec_priv`.

### Risks
Override masks can force unexpected register states and select the second output through a magic high bit. No readback or overload handling is implemented. I2C errors collapse to `-EIO`.

### Test Signals
Test attach detection, OFF/13V/18V for both outputs, LLC toggling, override_set/override_clear masks, release power-off, and I2C transfer failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/isl6405.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/isl6405.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/isl6405.h

### Purpose
`isl6405.h` declares the ISL6405 LNB supply register bit masks and attach API.

### Important APIs, Types, And Functions
The header defines system-register selector `ISL6405_SR`, output-1 bits such as `ISL6405_EN1`, `VSEL1`, `LLC1`, and output-2 bits such as `ISL6405_EN2`, `VSEL2`, `LLC2`. `isl6405_attach()` accepts a frontend, I2C adapter/address, and override set/clear masks.

### Control Flow
Enabled builds link to the real attach function. Disabled builds warn and return `NULL`.

### State, Persistence, And Dependencies
No state is stored here. The bit definitions are consumed by `isl6405.c` to build the cached config byte.

### Integration Points
Satellite frontends use this header to add SEC voltage control to an existing `dvb_frontend`.

### Risks
The same bit positions mean different things depending on `ISL6405_SR`; callers using override masks must understand which register bank is selected.

### Test Signals
Build with enabled/disabled Kconfig and validate override masks against both ISL6405 register maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/isl6405.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/isl6421.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/isl6421.c

### Purpose
`isl6421.c` implements LNB supply and SEC control for the Intersil ISL6421, including voltage selection, high-voltage line loss compensation, optional 22 kHz tone control, and overload protection.

### Important APIs, Types, And Functions
`struct isl6421` stores cached config, override masks, I2C adapter/address, and an `is_off` state flag. `isl6421_attach()` is exported. Core callbacks are `isl6421_set_voltage()`, `isl6421_enable_high_lnb_voltage()`, `isl6421_set_tone()`, and `isl6421_release()`.

### Control Flow
Attach allocates state, initializes current limit selection, stores masks, assigns `sec_priv`, probes by setting voltage off, marks off, and installs SEC callbacks. Voltage setting clears enable/voltage bits, maps OFF/13V/18V, temporarily disables dynamic current limiting when powering from off, writes then reads one byte, waits about one second if overload is flagged, re-enables dynamic current limiting when not forced, and disables power plus returns `-EINVAL` if overload persists.

### State, Persistence, And Dependencies
`config` is a cached one-byte register image. `is_off` records last known output power state for startup behavior. Dependencies include DVB SEC enums, I2C transfer, delays, and bit masks in `isl6421.h`.

### Integration Points
The driver overrides `fe->ops.set_voltage`, `enable_high_lnb_voltage`, and optionally `set_tone`; release is registered through `release_sec`.

### Risks
The probe write modifies hardware even when only detecting presence. `is_off` is updated before overload recovery, so failed writes can leave software and hardware out of sync. Tone override is optional and may conflict with demodulator tone support if configured incorrectly.

### Test Signals
Test voltage transitions from off to 13/18V, overload flag handling, DCL disable/reenable sequencing, high LNB voltage, optional tone override, release power-off, and I2C short-transfer paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/isl6421.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/isl6421.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/isl6421.h

### Purpose
`isl6421.h` defines ISL6421 system register bits and the LNB controller attach interface.

### Important APIs, Types, And Functions
Bit masks include overload flag, enable, voltage select, line loss compensation, tone enable, current select, and dynamic current limit. `isl6421_attach()` accepts override set/clear masks and an `override_tone` flag.

### Control Flow
The header only dispatches on Kconfig reachability, using a warning `NULL` stub when disabled.

### State, Persistence, And Dependencies
No state is stored. Runtime state is held by `isl6421.c` in `fe->sec_priv`.

### Integration Points
Satellite board drivers include this header when an ISL6421 provides LNB voltage/tone instead of the demodulator.

### Risks
Override masks can permanently force sensitive SEC bits. Disabled-Kconfig stubs require attach failure handling.

### Test Signals
Build enabled/disabled variants and verify board configs choose correct override masks and tone ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/isl6421.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/isl6423.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/isl6423.c

### Purpose
`isl6423.c` is an Intersil ISL6423 SEC/LNB power supply controller driver. It configures modulation input source, current limit, voltage, and voltage boost through one-byte I2C register writes.

### Important APIs, Types, And Functions
`struct isl6423_dev` stores the config pointer, I2C adapter, cached register 3 and 4 images, and verbose level. `isl6423_attach()` is exported. Helpers are `isl6423_write()`, `isl6423_set_modulation()`, `isl6423_set_current()`, `isl6423_set_voltage()`, `isl6423_voltage_boost()`, and `isl6423_release()`.

### Control Flow
Attach allocates state, seeds register selectors for SR3 and SR4, assigns `sec_priv`, programs current limit and modulation mode, then installs SEC callbacks. Current setup writes register 3 once for max current and again for DCL mode. Voltage setup adjusts enable, VTOP, VBOT, and VSPEN bits across cached registers and writes register 3 then register 4. Voltage boost forces enable/VSPEN and toggles VBOT.

### State, Persistence, And Dependencies
The cached register bytes are the main persistent driver state; hardware state follows successful writes. Dependencies include I2C transfer, DVB SEC voltage enums, module `verbose` logging, and `struct isl6423_config`.

### Integration Points
The driver owns `fe->sec_priv` and installs `release_sec`, `set_voltage`, and `enable_high_lnb_voltage`. It is used by satellite frontends needing external LNB supply control.

### Risks
Invalid voltage enum falls through and still writes the previous register state instead of returning `-EINVAL`. No readback or overload handling exists. Partial configuration failure frees state but may leave hardware registers changed.

### Test Signals
Test attach with each current limit and DCL setting, internal vs external modulation mode, OFF/13V/18V/boost writes, invalid voltage handling, I2C failure cleanup, and release power-off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/isl6423.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/isl6423.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/isl6423.h

### Purpose
`isl6423.h` declares configuration enums and attach API for the ISL6423 SEC/LNB controller.

### Important APIs, Types, And Functions
`enum isl6423_current` describes max-current selections from 275 mA through 800 mA. `enum isl6423_curlim` controls dynamic current limiting. `struct isl6423_config` carries current limit, current-limit mode, I2C address, and external modulation flag. `isl6423_attach()` attaches the controller to a frontend.

### Control Flow
Enabled Kconfig builds use the exported attach function; disabled builds warn and return `NULL`.

### State, Persistence, And Dependencies
No header state exists. The implementation stores the config pointer in `fe->sec_priv` state, so the config object must outlive the attached frontend.

### Integration Points
Satellite board drivers provide an `isl6423_config` when an ISL6423 supplies LNB voltage and modulation control.

### Risks
Config lifetime is caller-owned. Invalid enum values are not exhaustively checked by the implementation.

### Test Signals
Build enabled/disabled Kconfig, test all enum values, and validate board configs keep the config storage alive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/isl6423.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/itd1000.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/itd1000.c

### Purpose
`itd1000.c` implements the Integrant ITD1000 zero-IF DVB-S tuner. It initializes tuner registers, programs PLL local oscillator values, calibrates VCO, and adjusts baseband LPF/PGA from symbol rate.

### Important APIs, Types, And Functions
`itd1000_attach()` is exported. Register access helpers include `itd1000_write_regs()`, `itd1000_read_reg()`, and `itd1000_write_reg()`, backed by the shadow cache in `itd1000_state`. Tuning helpers are `itd1000_set_lpf_bw()`, `itd1000_set_vco()`, `itd1000_set_lo()`, and `itd1000_set_parameters()`. Static tables encode LPF/PGA choices, VCO ranges, RF tracking values, and init/reinit register sequences.

### Control Flow
Attach allocates state, reads register 0 and requires ID value 0, fills the shadow cache by reading registers `0x65` through `0x9b`, installs tuner ops, and stores `fe->tuner_priv`. Init writes the init and reinit tables. Set-params writes LO divider/fractional PLL registers, RF tracking registers selected by frequency, VCO coarse range adjusted by ADC feedback, LPF/PGA registers selected by symbol rate, then toggles a PLL control bit.

### State, Persistence, And Dependencies
`state->frequency` stores the actual programmed LO frequency in kHz. `state->shadow[256]` mirrors writes and is also used for a FlexCop I2C controller read workaround that rewrites the previous register before reading. Hardware register state persists across operations until retune/init.

### Integration Points
The driver fills `fe->ops.tuner_ops` for DVB-S demodulators. It depends on the private register enum header and `struct itd1000_config` for I2C address.

### Risks
Read failures return negative values but are stored into `u8` variables by many callers, so I2C errors can become bogus register values. LPF table lookup uses `< symbol_rate`; exact high-end values may skip intended rows. No real sleep implementation exists. The FlexCop workaround can write hardware during reads.

### Test Signals
Test chip ID detection, shadow initialization, init table writes, LO math across 950-2150 MHz, VCO ADC adjustment, symbol-rate LPF boundaries, I2C failure injection, and get-frequency reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/itd1000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/itd1000.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/itd1000.h

### Purpose
`itd1000.h` exposes the Integrant ITD1000 tuner configuration and attach API.

### Important APIs, Types, And Functions
`struct itd1000_config` contains the tuner I2C address. `itd1000_attach()` attaches tuner ops to a frontend, adapter, and config.

### Control Flow
Enabled builds call the exported attach function. Disabled builds warn and return `NULL`.

### State, Persistence, And Dependencies
No header state exists. The implementation stores the config pointer in tuner private state, so caller config storage must remain valid.

### Integration Points
DVB-S board drivers include this header to attach an ITD1000 tuner behind their demodulator.

### Risks
Only the I2C address is configurable; board-specific GPIO, clock, or gate handling must be outside the driver. Disabled stubs require caller-side failure handling.

### Test Signals
Build both Kconfig variants and verify board attach config lifetime and I2C address handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/itd1000.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/itd1000_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/itd1000_priv.h

### Purpose
`itd1000_priv.h` contains private state and register definitions for the ITD1000 tuner implementation.

### Important APIs, Types, And Functions
`struct itd1000_state` stores the config pointer, I2C adapter, last programmed frequency, and a 256-byte shadow register cache. `enum itd1000_register` names the register range used by initialization, PLL, VCO, RF tracking, gain, and reserved register programming.

### Control Flow
The header has no executable logic. `itd1000.c` uses the enum values for table-driven register writes and shadow-cache access.

### State, Persistence, And Dependencies
The shadow array is memory state used to work around controller read behavior and to preserve register values across writes. The enum documents register addresses from `0x65` through `0x9b`, including reserved values.

### Integration Points
Only the ITD1000 implementation should include this header; it is not a public board-driver interface.

### Risks
Reserved and undocumented register names are still programmed by the driver, so changing enum values or table alignment can break hardware. Shadow cache correctness is required for safe reads.

### Test Signals
Compile-check enum users, verify shadow cache is initialized before reads, and compare register traces against known-good ITD1000 initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/itd1000_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ix2505v.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ix2505v.c

### Purpose
`ix2505v.c` implements the Sharp IX2505V/B0017 DVB-S silicon tuner. It computes PLL, gain, charge pump, local oscillator band, and low-pass filter values from frontend frequency and symbol rate.

### Important APIs, Types, And Functions
`struct ix2505v_state` stores I2C adapter, config pointer, and cached frequency. `ix2505v_attach()` is exported. Helpers include `ix2505v_read_status_reg()`, `ix2505v_write()`, `ix2505v_set_params()`, `ix2505v_get_frequency()`, and release.

### Control Flow
Attach validates config, allocates state, optionally reads the status register for presence, installs tuner ops, and stores `fe->tuner_priv`. Set-params validates frequency against frontend range, chooses baseband gain and charge pump from config with defaults, computes divider values `N` and `A`, chooses local oscillator band by frequency, computes LPF code from symbol-rate-derived bandwidth, opens I2C gate, writes the full four-byte tuning sequence, writes byte 4 with test mode set, waits 10 ms, writes byte 4/5 with LPF bits, optionally waits `min_delay_ms`, and caches frequency.

### State, Persistence, And Dependencies
Runtime state is memory-only plus hardware register state. `frequency` backs get-frequency. Dependencies include DVB frontend property cache, optional I2C gate control, I2C transfer, and config values from `ix2505v.h`.

### Integration Points
The driver installs `fe->ops.tuner_ops` for satellite demodulators. It expects parent demodulator I2C gate control if the tuner sits behind a gate.

### Risks
The `tuner_write_only` config comment says it disables reads, but the implementation performs the presence read only when it is set. The presence check treats POR bit set as no tuner. I2C gate close is not issued after set-params writes. Return aggregation uses bitwise OR of write return codes. The `else` before final LPF selection is oddly indented but functionally binds to the last `if`.

### Test Signals
Test presence detection with read-capable and write-only boards, frequency boundary validation, PLL divider math, LPF code boundaries, gain/charge-pump overrides, I2C gate behavior, configured delay, and write failure propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ix2505v.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ix2505v.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ix2505v.h

### Purpose
`ix2505v.h` declares configuration and attach API for the Sharp IX2505V DVB-S tuner.

### Important APIs, Types, And Functions
`struct ix2505v_config` includes tuner I2C address, optional gain and charge-pump settings, post-tune minimum delay, and `tuner_write_only`. `ix2505v_attach()` attaches tuner ops to a frontend and adapter.

### Control Flow
Enabled Kconfig builds call the exported attach function. Disabled builds warn and return `NULL`.

### State, Persistence, And Dependencies
No header state exists. Runtime state stores a pointer to this config, so its lifetime must outlive the attached tuner.

### Integration Points
Satellite board drivers use this header to configure IX2505V-specific analog parameters and attach it behind a demodulator.

### Risks
The `tuner_write_only` field documentation conflicts with implementation behavior around reads. Misspelled gain documentation (`bB`) is harmless but indicates this should be validated against datasheet values.

### Test Signals
Build enabled/disabled variants, verify config lifetime, and exercise all gain/charge-pump/delay combinations used by boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/ix2505v.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/l64781.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/l64781.c

### Purpose
`l64781.c` is an LSI L64781 COFDM DVB-T demodulator driver. It probes/reset-configures the demodulator, programs TPS/AFC/timing values, delegates tuner programming, and reports lock and quality metrics.

### Important APIs, Types, And Functions
`struct l64781_state` stores I2C adapter, config pointer, embedded frontend, and a first-init flag. `l64781_attach()` is exported. Helpers include `l64781_writereg()`, `l64781_readreg()`, `reset_and_configure()`, `reset_afc()`, `apply_tps()`, `apply_frontend_param()`, `get_frontend()`, lock/BER/strength/SNR/ucblocks readers, `l64781_init()`, and `l64781_sleep()`.

### Control Flow
Attach sends a broadcast reset/configure write to I2C address `0x00`, verifies read behavior at the configured demod address, checks power-down register semantics, toggles power state, and installs ops. Init powers up, performs hard reset, configures ADC/AGC/format registers, and delays 200 ms only on the first init. Set-frontend validates bandwidth, inversion, FEC, modulation, transmission mode, guard interval, and hierarchy, calls the tuner, computes DDFS/init-frequency/SPI-bias values from bandwidth and TPS parameters, writes TPS registers, resets AFC, programs timing and bias registers, clears interrupts, and applies TPS.

### State, Persistence, And Dependencies
State is mostly hardware registers; only `first` changes init delay behavior. `get_frontend()` reconstructs cached properties from demod registers and adds AFC offset to frequency. Dependencies include I2C, DVB-T property cache, optional tuner ops and I2C gate control, and config address from the header.

### Integration Points
The demodulator owns frontend ops for DVB-T and can use an attached tuner through `fe->ops.tuner_ops`. The old reset/configure broadcast implies board-level I2C topology matters.

### Risks
Register read errors can be interpreted as data in several paths. `l64781_writereg()` returns `-1` rather than a normal errno. Broadcast reset may affect other bus devices if topology is unexpected. Tune delay is long at 4000 ms. Several calculations use fixed 8000 ppm assumptions and comments flag questionable TPS auto-update behavior.

### Test Signals
Test probe with and without real L64781, broadcast reset behavior on target boards, all DVB-T parameter validation paths, tuner delegation and gate close, status bit mapping, metric reads, sleep/power-up transitions, and AFC/frequency reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/l64781.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/l64781.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/l64781.h

### Purpose
`l64781.h` declares the LSI L64781 DVB-T demodulator configuration and attach API.

### Important APIs, Types, And Functions
`struct l64781_config` contains the demodulator I2C address. `l64781_attach()` returns a frontend for a config and I2C adapter.

### Control Flow
Enabled Kconfig builds call the exported attach function; disabled builds warn and return `NULL`.

### State, Persistence, And Dependencies
No state is stored here. The implementation stores the config pointer in private demodulator state.

### Integration Points
Board drivers include this header to instantiate an L64781 demodulator before attaching a tuner.

### Risks
Only I2C address is configurable despite the implementation having board-sensitive reset behavior. Callers must keep the config object valid.

### Test Signals
Build enabled/disabled Kconfig variants and verify attach failure handling by callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/l64781.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lg2160.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lg2160.c

### Purpose
`lg2160.c` implements LG2160/LG2161 ATSC-M/H demodulator support. It configures demodulator registers, tuner I2C repeater, IF/spectrum/AGC settings, output interface, parade and ensemble selection, FIC enablement, status, SNR, and ATSC-M/H metadata reporting.

### Important APIs, Types, And Functions
`struct lg216x_state` stores I2C adapter, config pointer, embedded frontend, current frequency, parade id, FIC version, and last reset timestamp. `lg2160_attach()` is exported. Important helpers include `lg216x_write_reg()`, `lg216x_read_reg()`, `lg216x_i2c_gate_ctrl()`, `lg216x_soft_reset()`, `lg216x_initialize()`, IF/AGC/spectrum/tuner-power helpers, `lg216x_set_parade()`, `lg216x_set_ensemble()`, output clock/interface helpers, `lg216x_enable_fic()`, numerous ATSC-M/H metadata readers, `lg2160_set_frontend()`, `lg216x_get_frontend()`, status and SNR readers.

### Control Flow
Attach allocates state, selects LG2160 or LG2161 ops, initializes cached FIC/parade state, sets default parade 1, and returns the frontend without probing hardware. Set-frontend delegates tuner tuning and closes the I2C gate, clears AGC fixes, sets AGC polarity and tuner-power-save polarity, configures IF and spectrum inversion, resets, disables tuner power save, configures SPI clock or output interface by chip type, writes parade and ensemble selection, runs chip initialization, enables FIC, then refreshes frontend metadata. `get_frontend()` returns ATSC-M/H properties and only rereads metadata when FIC version changes.

### State, Persistence, And Dependencies
Cached frequency, FIC version, parade ID, and last reset are in memory; demodulator registers hold hardware state. Dependencies include DVB ATSC-M/H property fields, tuner ops, I2C, jiffies timing, and `lg2160_config`.

### Integration Points
The frontend supports `SYS_ATSCMH` and exposes `i2c_gate_ctrl` for downstream tuners unless `deny_i2c_rptr` is set. Parent board configs select chip type, IF, inversion, SPI/output interface, and repeater behavior.

### Risks
No hardware detection occurs during attach. Several error counters and recovery code are compiled out, so `read_ucblocks()` and signal strength return zero. `lg2161_set_output_interface()` notes missing sanity checks. `lg2160_spectrum_polarity()` performs a soft reset even if the preceding read/write failed. Cached metadata updates only on FIC version changes.

### Test Signals
Test LG2160 and LG2161 attach configs, tuner delegation and repeater gating, IF zero/nonzero config, spectral inversion, SPI/output interface values, parade/ensemble selection, FIC metadata changes, lock bit mapping, SNR decoding, and I2C error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lg2160.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lg2160.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lg2160.h

### Purpose
`lg2160.h` exposes configuration and attach API for LG2160/LG2161 ATSC-M/H demodulators.

### Important APIs, Types, And Functions
`enum lg_chip_type` selects LG2160 or LG2161. `enum lg2160_spi_clock` selects LG2160 SPI clock. `struct lg2160_config` contains I2C address, IF frequency in kHz, repeater disable flag, spectral inversion flag, output interface, SPI clock, and chip type. `lg2160_attach()` returns a frontend.

### Control Flow
Enabled builds call the exported attach function. Disabled builds warn and return `NULL`.

### State, Persistence, And Dependencies
No state is stored in the header. The implementation keeps a pointer to `lg2160_config`, so caller storage must remain valid.

### Integration Points
Board drivers configure chip variant, IF/inversion, and output interface behavior through this header before registering the ATSC-M/H frontend.

### Risks
The disabled `lg2161_oif` enum means `output_if` is an untyped integer with limited compile-time validation. Aliases `LG2161_1019` and `LG2161_1040` both map to LG2161.

### Test Signals
Build Kconfig variants, validate config lifetime, and test each chip/output/clock configuration used by boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lg2160.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgdt3305.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgdt3305.c

### Purpose
`lgdt3305.c` implements LGDT3304/LGDT3305 ATSC 8VSB and Annex-B QAM demodulator support. It initializes chip-specific registers, configures modulation, AGC, IF NCO, spectral inversion, MPEG transport output, I2C repeater, lock reporting, SNR, signal strength, and uncorrected block counts.

### Important APIs, Types, And Functions
`struct lgdt3305_state` stores I2C adapter, config pointer, embedded frontend, current modulation/frequency, and 8.24-format SNR. `lgdt3305_attach()` is exported. Core helpers include 16-bit register read/write, `lgdt3305_soft_reset()`, MPEG mode/polarity setup, `lgdt3305_set_modulation()`, filter extension, passband digital AGC, RF/IF AGC loop setup, manual AGC power references, spectral inversion, IF NCO programming, init/sleep, chip-specific set-parameter functions, status readers, SNR calculation, strength scaling, and ucblocks.

### Control Flow
Attach allocates state, selects LGDT3304 or LGDT3305 ops, verifies hardware by reading `GEN_CTRL_2` and round-tripping register `0x0808`, then initializes current fields to invalid values. Init writes a chip-specific register table and soft-resets. Set-frontend delegates tuner tuning and closes the gate, sets modulation, AGC references, AGC loops, IF or fixed VSB NCO, spectral inversion, filter extension for LGDT3305, caches current modulation, configures MPEG mode and polarity, and soft-resets through `lgdt3305_mpeg_mode_polarity()`. Status combines general status, carrier-recovery lock, and QAM FEC lock or VSB in-lock.

### State, Persistence, And Dependencies
Cached modulation and frequency drive `get_frontend()` and status/SNR mode choices. `state->snr` backs signal-strength scaling. Hardware register state persists across init/tune/sleep. Dependencies include I2C, DVB frontend ATSC/QAM enums, `intlog10`, `do_div`, tuner ops, and `lgdt3305_config`.

### Integration Points
The frontend advertises `SYS_ATSC` and `SYS_DVBC_ANNEX_B`, exposes an I2C gate for tuners unless disabled, and supports board-specific IFs, MPEG transport polarity/mode, AGC behavior, and demod chip selection.

### Risks
`lgdt3305_write_regs()` iterates `i < len - 1`, apparently skipping the final table entry. Several helper writes ignore return values. `lgdt3305_read_status()` requires `current_modulation` to be valid, so status before tune can return `-EINVAL`. Attach failure warning formats chip name based on enum truthiness, which can be confusing. Manual AGC values and RF loop choices are board-sensitive.

### Test Signals
Test hardware detect, both chip init tables including skipped-last-entry behavior, VSB/QAM64/QAM256 tuning, tuner delegation and I2C gate, IF NCO math, AGC/manual-reference configs, MPEG polarity modes, sleep reset/tristate, status before and after tune, SNR/strength scaling, and ucblock register reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgdt3305.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgdt3305.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgdt3305.h

### Purpose
`lgdt3305.h` declares configuration knobs and attach API for LGDT3304/LGDT3305 ATSC/QAM-B demodulators.

### Important APIs, Types, And Functions
It defines MPEG transport mode, transport clock edge, clock mode, valid polarity, and chip-type enums. `struct lgdt3305_config` contains I2C address, QAM/VSB IFs, optional AGC power references, repeater-disable and spectral-inversion flags, RF AGC loop flag, transport output settings, and demod chip type. `lgdt3305_attach()` returns a frontend.

### Control Flow
Enabled builds use the exported attach function; disabled builds warn and return `NULL`.

### State, Persistence, And Dependencies
No header state exists. Runtime state retains a pointer to this config, so the config must outlive the frontend.

### Integration Points
Board drivers select LGDT3304 versus LGDT3305 and tune transport/AGC/IF behavior through this config before attaching tuners and registering the frontend.

### Risks
Zero AGC reference fields mean "use default" rather than literal zero. Bitfield flags and enum settings must match board wiring or transport output and tuner access can fail.

### Test Signals
Build enabled/disabled Kconfig, validate every board config, test QAM/VSB IF values, transport clock polarity/mode, RF AGC loop flag, and disabled repeater behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/lgdt3305.h -->
