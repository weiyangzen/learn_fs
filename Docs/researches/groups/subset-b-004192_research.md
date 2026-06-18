# Group Research: subset-b-004192

This grouped report covers Linux media tuner sources under `sources/distributed-fs/ceph-client/drivers/media/tuners`. Each section is source-tree aligned for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/msi001.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/msi001.c

Purpose: implements the Mirics MSi001 silicon tuner as an SPI-backed V4L2 subdevice. It exposes RF tuner operations and V4L2 RF tuner controls for bandwidth and gain, then converts requested RF frequency and controls into the chip's packed 24-bit SPI register writes.

Important APIs and types: `struct msi001_dev` owns the `spi_device`, `v4l2_subdev`, `v4l2_ctrl_handler`, individual control pointers, and cached `f_tuner`. Public integration is through `module_spi_driver(msi001_driver)`, `v4l2_spi_subdev_init()`, `v4l2_subdev_tuner_ops`, and `v4l2_ctrl_ops`. Main helpers are `msi001_wreg()`, `msi001_set_gain()`, `msi001_set_tuner()`, tuner callbacks, `msi001_s_ctrl()`, `msi001_probe()`, and `msi001_remove()`.

Control flow: probe allocates state, sets default frequency to the first band low edge, initializes the subdev, creates bandwidth auto/manual and gain controls, clusters bandwidth auto with bandwidth, and attaches the handler to the subdev. Frequency changes enter through `msi001_s_frequency()`, select one of two declared bands, clamp the input to the band range, cache it, and call `msi001_set_tuner()`. Tuning selects band mode/divider from `band_lut`, IF filter mode, clamps and rounds bandwidth to the chip-supported table, computes Fractional-N PLL values using `gcd()` and 64-bit division, writes a reset/config sequence, programs threshold/fraction/integer registers, reapplies gains, and writes final calibration-like constants. Gain controls call `msi001_set_gain()` directly with a mix of new `val` and committed `cur.val` values.

State and persistence: all persistent runtime state is in memory: cached `f_tuner`, control values, and the V4L2 control handler. No firmware, NVM, or filesystem persistence is used. Hardware state is entirely reconstructed by register writes on tune/control changes.

Dependencies and integration points: depends on SPI, V4L2 subdev/control APIs, `linux/gcd.h`, and media tuner control IDs. It is expected to be instantiated by an SPI device and registered as a tuner subdevice used by a parent bridge/receiver.

Risks: `msi001_wreg()` passes a host-endian `u32` buffer but writes only 3 bytes, so behavior depends on the intended wire byte order matching the platform/compiler layout. `bandwidth_auto` is clustered but `msi001_set_tuner()` always reads `dev->bandwidth->val`, making the auto flag mostly a V4L2 control-state convention rather than a separate algorithm. Tuning uses fixed IF `0`, fixed reference/divider assumptions, and no lock-status verification. Error handling is mostly immediate abort on SPI failure.

Test signals: exercise probe/remove, frequency clamping at both bands and the gap midpoint, all supported bandwidth roundups, gain control changes, SPI write ordering/counts, and failure propagation from `spi_write()`. Hardware or mocked-SPI tests should verify byte ordering of the 24-bit register format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/msi001.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mt2060.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/mt2060.c

Purpose: drives the Microtune MT2060 dual-conversion broadband DVB tuner over I2C. It supports legacy `mt2060_attach()` use and a modern I2C-driver probe path with platform data, identifies the chip, calibrates it, and exposes DVB tuner operations for init, sleep, tune, and frequency/IF reporting.

Important APIs and functions: raw helpers `mt2060_readreg()`, `mt2060_writereg()`, and `mt2060_writeregs()` perform single and chunked register transfers. `mt2060_set_params()` computes LO1/LO2 PLL programming from `dtv_property_cache.frequency`. `mt2060_calibrate()` writes static register presets and runs FM calibration. DVB callbacks include `mt2060_init()`, `mt2060_sleep()`, `mt2060_get_frequency()`, `mt2060_get_if_frequency()`, and `mt2060_release()`. Entry points are exported `mt2060_attach()` and the `i2c_driver` probe/remove table.

Control flow: attach/probe allocate `struct mt2060_priv`, fill configuration, verify `REG_PART_REV == PART_REV`, copy `mt2060_tuner_ops` into the frontend, and run calibration. Tuning opens the frontend I2C gate when available, primes `REG_LO1B1`, converts requested Hz to kHz, derives LO1 from requested RF plus IF1, rounds LO1 to 250 kHz and LO2 to 50 kHz, optionally applies disabled compile-time spur correction, maps input frequency to `lnaband`, writes registers `REG_LO1C1..REG_LO2C3`, then polls `REG_LO_STATUS` up to 10 times for both lock bits before closing the gate.

State and persistence: cached state includes actual tuned `frequency`, IF1 in MHz, optional calibration result `fmfreq`, adapter/client pointers, maximum I2C write chunk size, and whether the I2C-model sleep path is enabled. No persistent storage exists; calibration/tune writes program hardware state.

Dependencies and integration: uses Linux I2C, DVB frontend/tuner ops, optional `fe->ops.i2c_gate_ctrl`, module parameter `debug`, and platform data from `mt2060.h`. The I2C probe path enables deeper sleep via `REG_MISC_CTRL`; the legacy attach path leaves `sleep` false.

Risks: `mt2060_set_params()` does not return an error if lock polling times out, so callers may believe tuning succeeded without lock. Legacy `mt2060_attach()` does not close the I2C gate on early identification failures. I2C helper allocations are small but happen for every transfer in some paths. `mt2060_writeregs()` uses `priv->i2c_max_regs`; misconfigured zero would be dangerous, though both setup paths default or subtract to produce a usable value.

Test signals: verify register sequences for representative frequencies across all `lnaband` thresholds, I2C-gate open/close on success and failure, sleep/init behavior with `sleep` true/false, chunking with small `i2c_write_max`, chip-ID rejection, and lock-timeout observability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mt2060.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mt2060.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/mt2060.h

Purpose: public interface for the MT2060 tuner driver. It defines platform/configuration data used by board drivers and declares the legacy attach helper when the tuner driver is reachable by Kconfig.

Important APIs and types: forward declares `struct dvb_frontend` and `struct i2c_adapter`; defines `struct mt2060_platform_data` with `clock_out`, `if1`, `i2c_write_max`, and `dvb_frontend`; defines `struct mt2060_config` for legacy attach users with `i2c_address` and `clock_out`; declares `mt2060_attach()` or supplies a disabled-driver inline stub.

Control flow and integration: I2C-core users pass `mt2060_platform_data` via `client->dev.platform_data` to `mt2060_probe()`. Legacy board drivers call `mt2060_attach(fe, i2c, cfg, if1)` directly. The Kconfig guard uses `IS_REACHABLE(CONFIG_MEDIA_TUNER_MT2060)` so built-in and module linkage combinations get either the real symbol or a stub that logs a warning and returns `NULL`.

State and persistence: this header carries only configuration contracts; runtime state is private to `mt2060_priv.h` and `mt2060.c`.

Dependencies: relies on DVB frontend/I2C types, `u8`/`u16`, `printk()`, and `KERN_WARNING` from kernel headers included by consumers.

Risks: `i2c_write_max` is a 5-bit bitfield, which caps expressible values and requires callers to understand it is a byte-count limit where zero means default maximum. The `if1` platform-data value is documented in MHz and zero defaults to 1220; mismatch between board data units and driver expectations would mis-tune the PLL. The fallback stub compiles but only fails at attach time.

Test signals: compile both reachable and disabled Kconfig configurations, instantiate I2C platform-data probe with zero and nonzero `if1`/`i2c_write_max`, and validate old board code using `mt2060_config` still links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mt2060.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mt2060_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/mt2060_priv.h

Purpose: private MT2060 register map and state definition shared by the C implementation. It documents the inferred register layout from a Comtech SDVBT-3K6M tuner datasheet and centralizes constants used by the tuning and calibration code.

Important APIs/types: defines register offsets `REG_PART_REV` through `REG_LOTO`, chip ID `PART_REV 0x63`, default I2C address `0x60`, optional compile-time `MT2060_SPURCHECK`, and `struct mt2060_priv`. The private state contains the active config pointer, I2C adapter/client, embedded config for I2C-model devices, `i2c_max_regs`, cached tuned `frequency`, `if1_freq`, calibration `fmfreq`, and `sleep` feature flag.

Control flow integration: `mt2060.c` uses these register names for all raw reads/writes, PLL setup, calibration loops, and power management. The embedded `config` lets the I2C-driver path build a config from platform data while still using the same helper code as legacy attach.

State and persistence: describes in-memory state only. The `sleep` comment is important operational context: using `REG_MISC_CTRL` for sleep can reduce power materially, but is disabled by default for legacy attach because bit meanings are not fully known.

Dependencies: requires `mt2060_config`, `i2c_adapter`, `i2c_client`, fixed-width integer types, and `bool` from included kernel headers through the C file.

Risks: the register map has unknown/reserved fields and comments with uncertainty; any behavior changes around `REG_MISC_CTRL`, calibration, or reserved bytes need hardware validation. `PART_REV` hard-codes support to part 6/rev 3. Since private state stores raw pointers to board-supplied config, legacy callers must keep config memory alive as long as the frontend exists.

Test signals: verify register constants against transfer traces, cover ID mismatch, confirm `sleep` false on legacy attach and true on I2C probe, and test `i2c_max_regs` chunk behavior because it is private state but externally controlled via platform data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mt2060_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mt2063.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/mt2063.c

Purpose: implements the Micronas/Microtune MT2063 silicon tuner for DVB and analog frontend users. It initializes supported B0/B1/B2/B3 revisions, maintains a local register cache, selects receiver mode, computes dual-LO PLL values, avoids LO-related spurs, and exposes DVB tuner operations for digital tuning, analog tuning, status, IF, bandwidth, sleep, and release.

Important APIs and types: `struct mt2063_state` owns the I2C adapter, frontend, config, copied tuner ops, cached frequency/bandwidth/reference fields, chip ID, receiver mode, register cache, ClearTune table, and `MT2063_AvoidSpursData_t`. The implementation defines register offsets, power-mask bits, DNC output selection, receiver modes, default register tables, and many static helpers. Public entry is `mt2063_attach()`.

Control flow: attach allocates state, installs `mt2063_ops`, and defers hardware initialization. `mt2063_init()` reads and validates part/revision plus secondary ID, resets the tuner, writes revision-specific defaults, waits for FIFF calibration, reads all registers into cache, initializes spur-avoidance parameters and ClearTune thresholds, scales ClearTune values by FCU oscillator reading, enables software shutdown, clears power masks, and marks `init=true`. Digital `mt2063_set_params()` requires bandwidth, maps bandwidth to 6/7/8 MHz and delivery system to receiver mode, computes output IF and output bandwidth, sets receiver mode registers, and calls `MT2063_Tune()`. Analog tuning does similar calculations from V4L2 mode/std.

Tuning path: `MT2063_Tune()` validates RF and IF ranges, optionally programs ClearTune override, reads FIFF center, rounds requested first IF to LO step, resets exclusion zones, chooses first IF, computes LO1/LO2, calls `MT2063_AvoidSpurs()`, recalculates integer/fractional PLL terms, checks LO ranges, writes queued LO registers in the required order, updates FIFF offset if needed, polls lock status, and caches actual IF. Spur logic builds/merges exclusion zones for FracN and DECT avoidance, checks harmonics with overflow-conscious scaling and `gcd()`, and iteratively moves first IF until a spur-free point or band edge is reached.

State and persistence: state is volatile: register cache mirrors hardware after reads/writes, `init` gates public getters/tuning, `AS_Data` carries dynamic LO/IF/spur parameters, and `frequency` stores last requested frequency. No filesystem or firmware persistence exists.

Dependencies and integration: depends on DVB frontend ops, analog parameters, V4L2 standards, Linux I2C, `gcd()`, sleep delays, and optional frontend I2C gate callbacks. It is a legacy attach-only driver rather than an `i2c_driver`.

Risks: many helpers OR together status values; spur-avoidance returns positive informational bitmasks, while callbacks generally treat only negative status as failure, so positive flags can propagate in nonstandard ways. `mt2063_write()` uses a fixed 60-byte stack buffer and assumes callers keep writes below that. `mt2063_setreg()` updates cache only on success, but direct `mt2063_write()` users must update cache manually. B2 is accepted in ID switch but has no defaults table and falls through to `-ENODEV` during init. Several comments note FIXME or uncertainty around sleep and FM LO step.

Test signals: cover init for B0/B1/B3 and B2 rejection/default behavior, lock success/failure, digital DVB-T/DVB-C bandwidth choices, analog TV/radio IF calculations, spur-zone insertion/merge and unavoidable-spur status, ClearTune software mode, I2C-gate behavior, and cache consistency after failed writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mt2063.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mt2063.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/mt2063.h

Purpose: public header for the MT2063 tuner attach API. It exposes the minimal board-driver configuration needed by `mt2063.c`.

Important APIs/types: includes `<media/dvb_frontend.h>`, defines `struct mt2063_config` with `tuner_address` and `refclock`, and declares `mt2063_attach(struct dvb_frontend *fe, struct mt2063_config *config, struct i2c_adapter *i2c)` when `CONFIG_MEDIA_TUNER_MT2063` is reachable. Otherwise it provides a stub that logs a Kconfig-disabled warning and returns `NULL`.

Control flow and integration: board/front-end drivers construct `mt2063_config`, call `mt2063_attach()`, and then use the populated `fe->ops.tuner_ops`. The driver itself stores the config pointer in private state, so config lifetime must cover frontend lifetime.

State and persistence: no runtime state is stored here. `refclock` is accepted by the public config and copied into `state->reference` in attach, though the C implementation uses the fixed `MT2063_REF_FREQ` for its main tuning algorithm.

Dependencies: relies on DVB frontend definitions, I2C adapter declaration visibility from included kernel headers, fixed-width integer types, and Kconfig reachability.

Risks: mismatch between the exposed `refclock` and the implementation's fixed reference constant can confuse integrators expecting arbitrary reference-clock support. The disabled stub is only a runtime attach failure, not a compile failure. The trailing comment names `CONFIG_DVB_MT2063`, while the guard uses `CONFIG_MEDIA_TUNER_MT2063`, which is harmless but can mislead readers.

Test signals: build with tuner enabled/disabled, verify attach failure path for disabled configs, and validate board config lifetime and I2C address correctness in integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mt2063.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mt20xx.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/mt20xx.c

Purpose: legacy Microtune MT20xx analog tuner driver supporting MT2032 and MT2050 devices over the tuner-core I2C helper layer. It detects the part, installs chip-specific DVB tuner ops, computes PLL register values for TV/radio/digital-TV modes, and maintains the last tuned frequency.

Important APIs/types: `struct microtune_priv` stores `tuner_i2c_props`, XOGC, and cached `frequency`. Public entry is exported `microtune_attach()`. MT2032 helpers include `mt2032_compute_freq()`, `mt2032_set_if_freq()`, lock/VCO helpers, TV/radio setters, and `mt2032_init()`. MT2050 helpers include `mt2050_set_if_freq()`, antenna selection, TV/radio setters, and `mt2050_init()`. Common callbacks are `microtune_release()` and `microtune_get_frequency()`.

Control flow: attach allocates state, initializes tuner I2C properties, reads a 21-byte register block, extracts company/part/rev, dispatches to MT2032 or MT2050 initialization, names the tuner, and returns the frontend. MT2032 init writes programming-procedure defaults, adjusts crystal oscillator gain until XOK, and installs `mt2032_tuner_ops`. MT2032 tuning maps V4L2 analog parameters to RF Hz and IF2, computes LO1/LO2 divider/numerator fields from a 5.25 MHz reference, does a diagnostic spur check, writes selected register groups, polls lock with optional VCO optimization and LINT retry, then adjusts LOGC. MT2050 tuning computes two LOs from a 1.218 GHz first IF, writes six PLL bytes, and selects TV/radio antenna module parameters.

State and persistence: only `xogc` and last `frequency` persist in memory. Module parameters `debug`, `optimize_vco`, `tv_antenna`, and `radio_antenna` alter behavior globally for the module. Hardware state is programmed directly through I2C writes.

Dependencies and integration: depends on `tuner-i2c.h` helper APIs, DVB frontend tuner ops, V4L2 analog modes/stds, module parameters, and legacy tuner-core attach patterns.

Risks: unsupported detected parts return `NULL` without freeing the just-allocated private state. MT2032 spur checking only logs and does not retune away from spurs. Several I2C transfers log warnings but tuning often continues. Frequency math is old 32-bit integer code with manual scaling. Attach does not validate company code before part dispatch.

Test signals: detect MT2032/MT2050/unsupported parts, validate register writes for NTSC/PAL/radio/digital-TV paths, cover VCO optimization and lock retry, ensure unsupported attach frees or is handled by caller, test module parameter effects on antennas and VCO, and simulate I2C short writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mt20xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mt20xx.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/mt20xx.h

Purpose: public attach header for the legacy MT20xx Microtune driver.

Important APIs/types: includes Linux I2C and DVB frontend headers, declares `microtune_attach(struct dvb_frontend *fe, struct i2c_adapter *i2c_adap, u8 i2c_addr)` when `CONFIG_MEDIA_TUNER_MT20XX` is reachable, and provides a warning stub returning `NULL` otherwise.

Control flow and integration: board/tuner-core code calls `microtune_attach()` with a frontend, I2C adapter, and tuner I2C address. The C file detects the chip and populates `fe->ops.tuner_ops` with MT2032 or MT2050 operations.

State and persistence: no state is defined here; private state is in `mt20xx.c`.

Dependencies: relies on `struct dvb_frontend`, `struct i2c_adapter`, Kconfig reachability, `printk()`, and fixed-width integer types available through included kernel headers.

Risks: as an attach-only legacy interface, failures are signaled by `NULL`; callers must handle unsupported chips and disabled Kconfig gracefully. There is no public config structure for board-specific IF or antenna quirks; behavior is controlled by module parameters and hard-coded logic in the C file.

Test signals: build with enabled/disabled Kconfig, verify call sites handle `NULL`, and test that expected board code passes the correct I2C address.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mt20xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mt2131.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/mt2131.c

Purpose: implements the Microtune MT2131 QAM/8VSB single-chip tuner over I2C. It identifies supported chip IDs, writes initialization tables, computes PLL settings for requested digital frequency, reports lock/frequency status, and exports a legacy attach function.

Important APIs/functions: `struct mt2131_priv` is defined in the private header and stores config/I2C/frequency. I2C helpers are `mt2131_readreg()`, `mt2131_writereg()`, and `mt2131_writeregs()`. Main callbacks are `mt2131_init()`, `mt2131_set_params()`, `mt2131_get_frequency()`, `mt2131_get_status()`, and `mt2131_release()`. Entry point is `mt2131_attach()`.

Control flow: attach allocates private state, reads register 0, accepts IDs `0x3E` or `0x3F`, copies tuner ops, and stores private state on the frontend. Init writes a long config table, several direct register tweaks, then a second config table. Tuning converts requested Hz to kHz, computes LO1 as RF plus `MT2131_IF1`, rounds to 250 kHz, derives LO2 by subtracting RF and `MT2131_IF2`, caches actual tuned frequency, computes 13-bit fractional numerator and divider fields for both LOs from 16 MHz reference, selects an IF-band-center code from many RF thresholds, writes registers 1..6, writes the band-center register, and polls register `0x08` up to 10 times for both lock bits.

State and persistence: runtime state is limited to config pointer, I2C adapter, and cached actual frequency. No firmware or file persistence exists. Hardware programming is repeated on init/tune.

Dependencies and integration: uses raw Linux `i2c_transfer`, DVB frontend ops and cache, delays, module `debug`, and constants from `mt2131_priv.h`.

Risks: the `if1` attach parameter is unused; IF1 is fixed by private-header constants. `clock_out` in public config is also unused. Tune ignores errors from the IF-band-center write and lock polling timeout; it returns only the earlier bulk-write result. `get_status()` ignores read failures and may report unlocked with stale zeroes. The threshold ladder for IF band center is manual and should be hardware-verified.

Test signals: verify chip-ID accept/reject, init-table write lengths, PLL bytes for threshold-edge frequencies, lock polling behavior, propagation of I2C failures from all writes/reads, and callers that pass non-default `if1` or `clock_out`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mt2131.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mt2131.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/mt2131.h

Purpose: public configuration and attach interface for the MT2131 tuner.

Important APIs/types: forward declares DVB frontend and I2C adapter types; defines `struct mt2131_config` with `i2c_address` and `clock_out`; declares `mt2131_attach(fe, i2c, cfg, if1)` when the driver is reachable, otherwise provides a disabled-driver stub.

Control flow and integration: board drivers call `mt2131_attach()` with frontend, I2C adapter, config, and IF1 argument. The implementation validates chip ID and installs tuner ops on the frontend.

State and persistence: no runtime state is stored in the header. Config is consumed by private state in the C file, and callers must keep the config valid.

Dependencies: relies on Kconfig `CONFIG_MEDIA_TUNER_MT2131`, kernel logging for the stub, and fixed-width integer types.

Risks: both `clock_out` and the `if1` attach argument are exposed by the API but not used by the current implementation, which can mislead board authors. Disabled Kconfig produces a runtime warning/NULL rather than removing call sites.

Test signals: compile reachable/unreachable configurations, validate attach call sites handle `NULL`, and audit board data for assumptions about `clock_out` or non-default IF1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mt2131.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mt2131_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/mt2131_priv.h

Purpose: private MT2131 constants and state layout used by `mt2131.c`.

Important APIs/types: defines selected register aliases (`MT2131_PWR`, `MT2131_UPC_1`, `MT2131_AGC_RL`, `MT2131_MISC_2`), fixed frequency constants in kHz (`MT2131_IF1 1220`, `MT2131_IF2 44000`, `MT2131_FREF 16000`), and `struct mt2131_priv` with config pointer, I2C adapter pointer, and cached `frequency`.

Control flow and integration: the C file uses the IF/reference constants in PLL calculations and private state in every I2C/tuner callback. The register aliases are only partly used by name; several implementation writes still use raw numeric addresses.

State and persistence: private state is transient kernel memory attached to `fe->tuner_priv`; no persistent storage is involved.

Dependencies: requires `struct mt2131_config`, `struct i2c_adapter`, and integer types supplied through the including C file/header chain.

Risks: IF constants are hard-coded despite the public attach function accepting `if1`. Register aliases are sparse, so raw numeric register writes in the C file remain harder to audit. Unit comments say kHz, and calculations depend on that unit convention.

Test signals: verify PLL calculations when constants are changed, check all raw register writes against aliases/documentation, and confirm private frequency cache matches the tuned RF after rounding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mt2131_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mt2266.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/mt2266.c

Purpose: drives the Microtune MT2266 direct-conversion low-power broadband tuner over I2C for DVB frontend users. It handles chip identification, calibration, VHF/UHF band switching, bandwidth preset writes, PLL tuning, sleep/init power writes, and frequency/bandwidth reporting.

Important APIs/functions: private `struct mt2266_priv` stores config, I2C adapter, cached frequency/bandwidth, and current band. Raw helpers are `mt2266_readreg()`, `mt2266_writereg()`, and `mt2266_writeregs()`. Tuner callbacks are `mt2266_set_params()`, `mt2266_init()`, `mt2266_sleep()`, `mt2266_get_frequency()`, `mt2266_get_bandwidth()`, and `mt2266_release()`. Public entry is exported `mt2266_attach()`.

Control flow: attach allocates state, defaults band to UHF, reads part/rev register, requires `0x85`, copies tuner ops, stores private state, and runs `mt2266_calibrate()`. Calibration toggles control registers, writes init tables, sets 8 MHz defaults, and uses delays around analog calibration state changes. `mt2266_set_params()` converts the cached `priv->frequency` to kHz, rejects the VHF/UHF gap, stores requested frequency, computes a tune word from 30 MHz reference, doubles it for VHF, writes bandwidth table based on requested bandwidth, switches hardware tables if band changes, maps UHF frequency to LNA band code, writes tune registers, optionally writes UHF band/LNA registers, polls lock register, finalizes a VHF-to-UHF transition, and updates cached band.

State and persistence: keeps last frequency, bandwidth, and band in memory. Hardware state persists only until next power/reset and is reconstructed by init/calibration/tune writes.

Dependencies and integration: uses raw Linux I2C, DVB frontend property cache, delays, module debug parameter, and the public `mt2266_config` address.

Risks: `mt2266_set_params()` computes `freq` from `priv->frequency` before assigning `c->frequency`, so the first tune after attach or any tune uses the previous cached frequency for validation and PLL math. This looks like a likely bug; it should probably use `c->frequency / 1000`. Many writes ignore return values, lock timeout does not become an error, and the gap check may operate on stale data. Bandwidth defaults to 7 MHz for unknown values.

Test signals: first-tune behavior from zero cached frequency, subsequent retunes across VHF/UHF boundary, gap rejection using requested frequency, bandwidth table selection, calibration sequence, I2C failure propagation, and lock-timeout reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mt2266.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mt2266.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/mt2266.h

Purpose: public attach/config header for the MT2266 tuner.

Important APIs/types: forward declares DVB frontend and I2C adapter types; defines `struct mt2266_config` with `i2c_address`; declares `mt2266_attach(struct dvb_frontend *fe, struct i2c_adapter *i2c, struct mt2266_config *cfg)` when `CONFIG_MEDIA_TUNER_MT2266` is reachable; otherwise provides a logging stub returning `NULL`.

Control flow and integration: board drivers provide the I2C address through config and call attach. The implementation identifies the chip, installs tuner ops, and calibrates immediately.

State and persistence: no runtime state in the header; private state is allocated by `mt2266.c`.

Dependencies: Kconfig reachability, kernel logging, fixed-width integer types, and DVB/I2C type declarations.

Risks: configuration is intentionally minimal, so board-specific bandwidth, reference, or band behavior cannot be expressed through this API. Disabled-driver behavior is a runtime attach failure. The trailing Kconfig comment uses old-style naming but matches intent.

Test signals: enabled/disabled Kconfig builds, attach call-site `NULL` handling, and board configs with nondefault I2C addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mt2266.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mxl301rf.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/mxl301rf.c

Purpose: implements an incomplete MaxLinear MxL301RF OFDM tuner I2C driver. It provides basic wake/sleep, tuning, and RF-strength reporting, but explicitly relies on parent device firmware/card code to perform undisclosed chip initialization before this driver's `init()`.

Important APIs/types: `struct mxl301rf_state` embeds public config and `i2c_client`. I2C helpers are `raw_write()`, `reg_write()`, and `reg_read()`; `reg_read()` uses a `0xfb, reg` address-selection write before receiving one byte. DVB callbacks are `mxl301rf_init()`, `mxl301rf_sleep()`, `mxl301rf_set_params()`, and `mxl301rf_get_rf_strength()`. The Linux `i2c_driver` probe/remove functions attach state to the DVB frontend.

Control flow: probe allocates state, copies platform config, stores frontend private data, copies tuner ops, and stores a clientdata pointer to embedded config. Init only writes register `0x01=0x01` to wake the tuner. Tuning writes an abort/config sequence, optionally modifies spur-shift placeholder registers from `shf_tab` if requested frequency is near a listed center, converts frequency to a 10.6 fixed-point MHz value for RF registers `0x11/0x12`, starts tuning, waits 31 ms, writes `0x1a=0x0d`, and writes an IDAC sequence. Sleep writes standby register pairs. RF strength triggers measurement, reads RF input/offset registers, calculates dBm in millidecibels for the DVB stats cache, and returns a percentage approximation through the legacy `u16 *out`.

State and persistence: only frontend/client pointers and copied config are stored. The driver does not cache frequency, bandwidth, or full register state. The parent is responsible for persistent or firmware-provided initialization.

Dependencies and integration: uses Linux I2C client model, DVB frontend stats/property cache, platform data `struct mxl301rf_config`, and is noted as currently dependent on PT3-style parent initialization.

Risks: no null check for `client->dev.platform_data` before `memcpy()`. The packed register arrays are cast to `u8 *`, relying on `struct reg_val` being exactly two packed bytes. Tuning supports only fixed bandwidth register value and no IF-frequency callback. Initialization is intentionally incomplete, so this driver is not standalone. RF-strength percentage math can produce values outside common expectations if raw readings exceed assumed range.

Test signals: probe with missing/valid platform data, parent-init sequencing, raw I2C short write/read handling, spur-shift table matches at threshold edges, fixed-point frequency conversion rounding, RF strength stats scale/value, and remove clearing `fe->tuner_priv`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mxl301rf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mxl301rf.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/mxl301rf.h

Purpose: public platform-data header for the MxL301RF I2C tuner driver.

Important APIs/types: includes `<media/dvb_frontend.h>` and defines `struct mxl301rf_config` containing only `struct dvb_frontend *fe`.

Control flow and integration: parent I2C-board registration passes this config as `client->dev.platform_data`; `mxl301rf_probe()` copies it, uses `fe` to install tuner ops, and stores private state in `fe->tuner_priv`.

State and persistence: no runtime state is declared here beyond the frontend pointer contract. All private state is in `mxl301rf.c`.

Dependencies: requires DVB frontend definitions and a parent driver that already knows how to initialize/configure the chip outside this header's contract.

Risks: the config cannot express I2C address, IF, clock, bandwidth capabilities, or init tables; those are assumed to come from I2C device registration and parent-specific firmware/init code. Because the C probe blindly dereferences platform data, callers must always provide a valid `mxl301rf_config`.

Test signals: probe registration with valid platform data, missing-platform-data robustness if fixed, and integration with the parent card driver that performs undisclosed initialization before tuner init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mxl301rf.h -->
