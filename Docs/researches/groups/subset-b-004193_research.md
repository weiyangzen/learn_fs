# subset-b-004193 research

Work item: `subset-b-004193`

This grouped report covers Linux media tuner drivers under `sources/distributed-fs/ceph-client/drivers/media/tuners/`. Each section is delimited for reconciliation into one source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mxl5005s.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/mxl5005s.c

## Purpose
`mxl5005s.c` is the Linux DVB tuner driver for the MaxLinear MXL5005S VSB/QAM/DVB-T silicon tuner. It adapts a large MaxLinear/Realtek reference-register implementation to the LinuxTV `dvb_tuner_ops` API. The driver programs initialization controls, RF/IF/TG synthesizers, AGC, RSSI, baseband filters, GPIO-driven tracking filters, and modulation-specific register values, then exposes tuning, cached frequency/bandwidth/IF reads, init, and release operations.

## Important APIs, types, and functions
The private state is `struct mxl5005s_state`, which stores board config, frontend and I2C adapter pointers, software register/control tables, selected mode, IF/RF/TG frequencies, AGC/filter options, and cached `current_mode`. Internal table abstractions are `struct TunerReg` and `struct TunerControl`. Public integration is `mxl5005s_attach()`, which allocates state, installs `mxl5005s_tuner_ops`, and stores `fe->tuner_priv`.

Key entry points are `mxl5005s_init()`, `mxl5005s_set_params()`, `mxl5005s_get_frequency()`, `mxl5005s_get_bandwidth()`, `mxl5005s_get_if_frequency()`, and `mxl5005s_release()`. Core programming helpers include `mxl5005s_reset()`, `mxl5005s_writereg()`, `mxl5005s_writeregs()`, `mxl5005s_reconfigure()`, `mxl5005s_AssignTunerMode()`, and `mxl5005s_SetRfFreqHz()`. The reference-driver layer is built around `MXL5005_RegisterInit()`, `MXL5005_ControlInit()`, `MXL5005_ControlInitCH()`, `MXL5005_TunerConfig()`, `MXL_BlockInit()`, `MXL_IFSynthInit()`, `MXL_TuneRF()`, `MXL_ControlWrite()`, `MXL_ControlWrite_Group()`, `MXL_RegWriteBit()`, and register export helpers such as `MXL_GetInitRegister()` and `MXL_GetCHRegister()`.

## Control flow
Attach is lightweight: no chip probe is performed, and the frontend immediately receives tuner ops. `mxl5005s_init()` sets a default QAM mode and calls `mxl5005s_reconfigure()`. Reconfiguration resets the chip, allocates address/data tables, writes a master-control synth-reset byte ORed with `config->AgcMasterByte`, assigns the requested tuner mode, derives initialization registers through `MXL_GetInitRegister()`, and writes the table over I2C. Tuning starts in `mxl5005s_set_params()`, which maps `delivery_system` and bandwidth to MaxLinear modulation and 6/7/8 MHz bandwidth constants. If modulation or bandwidth changed, it reconfigures before calling `mxl5005s_SetRfFreqHz()`. RF tuning writes synth reset, invokes `MXL_TuneRF()` to populate channel-change register shadows, reads channel register lists, appends master-control bytes, and writes the resulting sequence.

The synthesizer path is highly table and range driven. `MXL_SynthIFLO_Calc()` derives IF LO from digital or analog IF mode. `MXL_SynthRFTGLO_Calc()` derives RF LO and tracking-generator LO from input RF and analog/digital mode. `MXL_IFSynthInit()` recognizes many fixed IF frequencies, sets divider/VCO bias values, and calculates integer/fractional IF modulation values. `MXL_TuneRF()` validates RF LO/TG LO ranges, selects downconverter and RF/TG divider settings from frequency ranges, computes fractional synthesizer values, applies QAM gain overrides, and configures off-chip tracking filter banks through DAC and GPIO controls.

## State and persistence
All persistent runtime state lives in `fe->tuner_priv`. Hardware state is mirrored in `state->TunerRegs`, `Init_Ctrl`, and `CH_Ctrl`; `MXL_ControlWrite()` updates those shadows, and `mxl5005s_writeregs()` flushes selected register lists to the device. Cached query state is `RF_IN`, `Chan_Bandwidth`, and `IF_OUT`. There is no suspend-resume persistence beyond reinitializing and reprogramming the chip. Dynamic allocations in reconfigure are freed before return, while the main state is freed in `.release`.

## Dependencies and integration points
The driver depends on Linux kernel module, slab, delay, I2C, and DVB frontend APIs plus `mxl5005s.h`. It honors `fe->ops.i2c_gate_ctrl` around I2C access. Integration is via direct attach, not an `i2c_driver`. Module metadata exports `mxl5005s_attach()` with GPL linkage. Board behavior is controlled entirely by `struct mxl5005s_config` from the caller.

## Risks and test signals
The code has large hardware tables and many magic constants inherited from vendor/reference code, so regressions are likely to be hardware-specific. Attach does not verify chip presence. Several status accumulators add unsigned return values from helpers that may return `-1`, which makes error propagation imprecise. `mxl5005s_reconfigure()` ignores return values from reset and table writes, so some I2C failures may only surface during later tuning. Important tests are compile coverage for all Kconfig states, attach/init/tune smoke tests on boards using ATSC, Annex B QAM, and DVB-T 6/7/8 MHz, validation of I2C gate pairing, and RF lock/IF output checks across the documented frequency and tracking-filter ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mxl5005s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mxl5005s.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/mxl5005s.h

## Purpose
`mxl5005s.h` is the public board-integration header for the MaxLinear MXL5005S tuner driver. It defines the configuration contract consumed by `mxl5005s_attach()` and exposes a Kconfig-gated attach prototype or stub.

## Important APIs and types
The central type is `struct mxl5005s_config`. It carries the 7-bit I2C address, IF and crystal frequency selections, AGC mode, tracking-filter type, RSSI/capacitor/clock/divider options, IF output load, AGC take-over point, analog/digital mode, IF mode, optional QAM gain override, and `AgcMasterByte`. The header defines legal symbolic values for common IFs, crystals, AGC modes, tracking filters, RSSI enablement, capacitor selection, divider/clock output, output loads, TOP values, modulation mode, and zero/low IF mode.

The exported API is `mxl5005s_attach(struct dvb_frontend *fe, struct i2c_adapter *i2c, struct mxl5005s_config *config)`. When `CONFIG_MEDIA_TUNER_MXL5005S` is not reachable, the inline stub logs that the driver is disabled and returns `NULL`.

## Control flow and integration
Board drivers include this header, fill `struct mxl5005s_config`, and call attach during frontend setup. The `.c` file reads these fields when assigning tuner mode and when deciding IF synthesizer, AGC, RSSI, clock, and tracking-filter behavior. The header does not own runtime control flow; it defines all board-specific policy fed into the implementation.

## State and persistence
The config object is not copied by the implementation; `mxl5005s_attach()` stores the pointer in private state. Callers must keep the config storage valid for the lifetime of the frontend. No mutable state is declared here, but fields such as `qam_gain` and `AgcMasterByte` materially change later register programming.

## Dependencies
The header depends on `<linux/i2c.h>` and `<media/dvb_frontend.h>`. It uses `IS_REACHABLE()` to make the attach API safe for built-in/module combinations.

## Risks and test signals
Many fields are unvalidated enums represented as integer types, so invalid board data can select unsupported register values or leave synthesizer paths with no matching case. The pointer-lifetime contract is implicit. Test signals include building with tuner support enabled and disabled, verifying no caller passes stack-local config data, and checking board configs against the defined IF, XTAL, TOP, mode, and tracking-filter constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mxl5005s.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mxl5007t.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/mxl5007t.c

## Purpose
`mxl5007t.c` implements the MaxLinear MxL5007T silicon tuner driver for DVB/ATSC/cable frontends. It converts frontend delivery-system and bandwidth requests into MxL5007T init and RF-tune register tables, performs I2C programming, reports synth-lock status, and supports shared hybrid tuner instances.

## Important APIs, types, and functions
The private type is `struct mxl5007t_state`, containing a `hybrid_tuner_instance_list` node, `tuner_i2c_props`, per-device mutex, config pointer, chip revision, mutable copies of init/cable/rftune register tables, selected IF enum, and cached frequency/bandwidth. Local enums model tuner mode, chip revision, and bandwidth. `struct reg_pair_t` is the table format.

Primary external API is `mxl5007t_attach()`. Tuner ops include `.init`, `.sleep`, `.set_params`, `.get_status`, `.get_frequency`, `.get_bandwidth`, `.get_if_frequency`, and `.release`. Important helpers are `set_reg_bits()`, `copy_reg_bits()`, `mxl5007t_set_mode_bits()`, `mxl5007t_set_if_freq_bits()`, `mxl5007t_set_xtal_freq_bits()`, `mxl5007t_calc_init_regs()`, `mxl5007t_calc_rf_tune_regs()`, `mxl5007t_write_reg()`, `mxl5007t_write_regs()`, `mxl5007t_read_reg()`, `mxl5007t_soft_reset()`, `mxl5007t_tuner_init()`, `mxl5007t_tuner_rf_tune()`, `mxl5007t_synth_lock_status()`, and `mxl5007t_get_chip_id()`.

## Control flow
Attach is serialized by `mxl5007t_list_mutex` and uses `hybrid_tuner_request_state()` to allocate or reuse a state for the I2C adapter/address pair. New instances initialize the state mutex and read chip ID register `0xd9`; all attach calls perform soft reset and write loop-through enable to register `0x04`. `mxl5007t_set_params()` maps `SYS_ATSC`, `SYS_DVBC_ANNEX_B`, `SYS_DVBT`, and `SYS_DVBT2` to tuner mode and 6/7/8 MHz bandwidth. It opens the frontend I2C gate, locks the state mutex, writes a freshly calculated init table, writes a calculated RF tune table, and updates cached frequency/bandwidth.

Register calculation is staged. Init tables begin from static defaults, then mode, IF frequency/inversion, crystal frequency, clock output, and cable-specific settings are patched. RF tune calculation patches bandwidth bits and converts RF frequency to a 16-bit fixed-point MHz value with a 10-bit integer and 6-bit fractional representation. Status reads register `0xd8` and sets `TUNER_STATUS_LOCKED` when either RF or reference lock bits are set.

## State and persistence
The driver stores mutable register-table copies in the private state rather than writing the static templates directly. The config pointer is retained, not copied. `state->if_freq` records the configured IF enum for later `.get_if_frequency`, while `state->frequency` and `state->bandwidth` are updated after successful tuning. Hybrid instance reference management is delegated to `hybrid_tuner_release_state()`.

## Dependencies and integration points
The implementation depends on Linux I2C, V4L2 type constants, DVB frontend APIs, `tuner-i2c.h`, and `mxl5007t.h`. It uses frontend I2C gate callbacks around all hardware access and exports `mxl5007t_attach()`. Board drivers provide I2C address and `struct mxl5007t_config`.

## Risks and test signals
The config pointer lifetime is external. `copy_reg_bits()` does not reset its inner index for each outer row, so it relies on sorted/compatible table ordering and would be fragile if table layout changes. `mxl5007t_get_status()` treats either RF or ref lock as tuner locked, which may be looser than hardware expectations. Tuning reinitializes on each parameter set, which is simple but may increase lock time. Test signals include chip-ID detection, loop-through writes, set-params for ATSC, Annex B, DVB-T/T2 bandwidths, IF frequency reporting for every enum, status register interpretation, hybrid multi-frontend reference behavior, and disabled-Kconfig stub builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mxl5007t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mxl5007t.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/mxl5007t.h

## Purpose
`mxl5007t.h` declares the board-facing configuration and attach API for the MaxLinear MxL5007T tuner driver. It lets demod/bridge drivers select IF, crystal, clock output, loop-through, and inversion behavior without depending on implementation internals.

## Important APIs and types
`enum mxl5007t_if_freq` lists supported IF choices from 4 MHz through 44 MHz. `enum mxl5007t_xtal_freq` lists crystal frequencies from 16 MHz through 49.3811 MHz. `enum mxl5007t_clkout_amp` selects clock-output amplitude. `struct mxl5007t_config` includes signed IF differential output level, clock output amplitude, crystal enum, IF enum, and bitfields for IF inversion, loop-through enable, and clock output enable.

The public API is `mxl5007t_attach(struct dvb_frontend *fe, struct i2c_adapter *i2c, u8 addr, struct mxl5007t_config *cfg)`. A disabled-driver inline stub prints a warning and returns `NULL`.

## Control flow and integration
Consumers include this header during frontend setup and call attach with a live frontend, adapter, I2C address, and persistent config. The implementation uses the IF and XTAL enums to patch init register tables, loop-through in attach, and clock settings during init table calculation. The header itself contains no executable tuning logic.

## State and persistence
The implementation stores a pointer to `struct mxl5007t_config`, so caller-owned config must outlive the tuner instance. The bitfields are compact ABI-facing inputs but not persisted in hardware until attach/init/set-params paths write the register tables.

## Dependencies
The header depends on `<media/dvb_frontend.h>` and references `struct i2c_adapter`. Its Kconfig guard uses `IS_REACHABLE(CONFIG_MEDIA_TUNER_MXL5007T)`.

## Risks and test signals
The enums expose only values known to the implementation; unsupported board values cannot be represented cleanly except by invalid enum casts. `if_diff_out_level` is not range-checked in the header and is used arithmetically for cable mode. Test signals include all Kconfig combinations, caller configs using each supported IF/XTAL pair in existing boards, loop-through and clock-out behavior, and static analysis for config lifetime.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/mxl5007t.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/qm1d1b0004.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/qm1d1b0004.c

## Purpose
`qm1d1b0004.c` implements an I2C client driver for the Sharp QM1D1B0004 satellite tuner. It is intentionally narrow, reflecting limited public chip documentation and assumptions inherited from VA1J5JF8007S/Earthsoft PT1/PT2 usage. It attaches tuner ops to a DVB frontend and programs PLL, band/pre-scaler bits, and LPF settings for 950 to 2150 MHz satellite tuning.

## Important APIs, types, and functions
Private state is `struct qm1d1b0004_state`, holding a copied `struct qm1d1b0004_config` and the `i2c_client`. `struct qm1d1b0004_cb_map` maps upper frequency thresholds to control-byte values that encode band, divider, and pre-scaler state. The main helpers are `lookup_cb()`, `qm1d1b0004_set_params()`, `qm1d1b0004_set_config()`, `qm1d1b0004_init()`, `qm1d1b0004_probe()`, and `qm1d1b0004_remove()`. `qm1d1b0004_ops` exposes `.init`, `.set_params`, and `.set_config`.

## Control flow
Probe receives `struct qm1d1b0004_config` via `client->dev.platform_data`, extracts the frontend, allocates state, installs tuner ops, stores the client, copies config, and registers frontend private state. Init writes a two-byte startup sequence, adding the half-step bit if configured. Tuning reads `fe->dtv_property_cache.frequency`, computes PLL step from the 4 MHz crystal divided by 4 and optionally by 2 for half-step mode, rounds the divider word, and adjusts it if the selected band uses the pre-scaler bit. Programming then sends a four-byte frequency setup with BG/TM/LPF defaults, sends a one-byte TM enable, waits 20 ms, computes LPF from configured `lpf_freq` or symbol rate fallback, writes LPF bits, and finally reads one byte that is described as possible PLL-lock status but is not interpreted.

## State and persistence
Runtime state is minimal. The config is copied into private state and can be replaced by `.set_config`. No tuned frequency, LPF, or lock state is cached for getter APIs. Hardware state persists only in the tuner registers until reinit or retune.

## Dependencies and integration points
The driver depends on Linux kernel/module headers, DVB frontend APIs, I2C client APIs, and `qm1d1b0004.h`. It uses `module_i2c_driver()` and identifies devices by the `"qm1d1b0004"` I2C ID. Frontend linkage is through platform data, `fe->tuner_priv`, and copied `dvb_tuner_ops`.

## Risks and test signals
The code assumes valid platform data and does not explicitly null-check `cfg` or `cfg->fe`. The final read does not validate lock bits, so tuning may report success even if the PLL did not lock. Partial positive `i2c_master_send()` returns are not converted to `-EIO`, unlike some newer drivers. Hardware behavior is underdocumented and board-specific. Test signals include probe/remove lifecycle, tuning at each band threshold, half-step divider behavior, symbol-rate-derived LPF fallback, zero symbol-rate fallback to 30 MHz LPF, and I2C short-transfer/error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/qm1d1b0004.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/qm1d1b0004.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/qm1d1b0004.h

## Purpose
`qm1d1b0004.h` defines the platform-data contract for the Sharp QM1D1B0004 satellite tuner I2C driver.

## Important APIs and types
`struct qm1d1b0004_config` contains the `struct dvb_frontend *fe` to modify during probe, optional `lpf_freq` in kHz, and a `half_step` boolean selecting 500 Hz PLL steps instead of 1000 Hz steps. `QM1D1B0004_CFG_PLL_DFLT` and `QM1D1B0004_CFG_LPF_DFLT` are sentinel values indicating default behavior; the PLL sentinel is declared for symmetry even though the current config structure has no PLL frequency field.

## Control flow and integration
Bridge or PCI/frontend code passes this structure through `i2c_board_info.platform_data` or equivalent I2C client creation. The `.c` probe uses `cfg->fe` to install tuner ops, and `.set_params` uses `lpf_freq` and `half_step` when calculating PLL and LPF bytes.

## State and persistence
The implementation copies the config into private state during probe and during `.set_config`, so the caller's platform-data object does not need to remain mutable after setup. The frontend pointer inside the copied config remains authoritative for removal and logging contexts.

## Dependencies
The header depends only on `<media/dvb_frontend.h>` for `struct dvb_frontend` and kernel integer/bool types pulled by the media headers.

## Risks and test signals
There is no attach stub because this is an `i2c_driver`-style tuner, not a direct attach helper. Callers must pass a valid frontend pointer. Tests should cover default LPF sentinel behavior, half-step configuration, I2C client creation with platform data, and compile coverage for users that include only this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/qm1d1b0004.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/qm1d1c0042.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/qm1d1c0042.c

## Purpose
`qm1d1c0042.c` implements an I2C client DVB tuner driver for the Sharp QM1D1C0042 8PSK satellite tuner. It programs a small cached register map, supports LPF and fast-search tuning modes, and exposes init, sleep, config, and set-params operations. The file explicitly notes limited chip documentation and PT3-specific assumptions.

## Important APIs, types, and functions
The private state is `struct qm1d1c0042_state`, holding a copied config, `i2c_client`, and a 0x20-byte register shadow. `reg_initval` contains two possible initial register rows selected by chip ID. `default_cfg` supplies xtal, LPF, fast-search, and wait defaults. Key functions are `cfg_to_state()`, `reg_write()`, `reg_read()`, `qm1d1c0042_set_srch_mode()`, `qm1d1c0042_wakeup()`, `qm1d1c0042_set_config()`, `qm1d1c0042_set_params()`, `qm1d1c0042_sleep()`, `qm1d1c0042_init()`, `qm1d1c0042_probe()`, and `qm1d1c0042_remove()`.

## Control flow
Probe allocates state, stores the I2C client, obtains frontend/config from platform data, assigns `fe->tuner_priv`, applies config defaults, installs tuner ops, and stores a pointer to the embedded config as client data. Init performs a repeated soft-reset sequence, reads register `0x00`, selects a matching `reg_initval` row, copies it into the shadow, writes calibration/setup registers, wakes the chip, and applies fast-search mode. Sleep clears baseband register enable, sets standby and PFD reset bits, then writes affected registers.

Tuning reads frequency from `fe->dtv_property_cache`, selects divider/VCO band parameters from `conv_table`, writes integer divider registers, optionally enables LPF clock/filter settings, calculates the fractional sigma-delta value with 64-bit math, toggles VCO/LPF tune mode bits, waits according to LPF/fast/normal mode, and finalizes LPF and CSEL offset programming. `set_config()` ignores non-default `xtal_freq` with a warning and always uses the 16 MHz default, but applies LPF, fast-search, and wait settings.

## State and persistence
The register shadow is the source of truth for masked updates; every tuning path mutates `state->regs` and then writes selected bytes. Config is copied into state and can be updated through `.set_config`. There are no frequency getters or lock-status caches. The global `reg_index` records the selected init row, which is not per-device and could be surprising if multiple variants coexist.

## Dependencies and integration points
The driver uses Linux kernel, math64, I2C, and DVB frontend APIs plus `qm1d1c0042.h`. It is registered with `module_i2c_driver()` under I2C ID `"qm1d1c0042"`. It integrates with a parent frontend through platform data and `fe->ops.tuner_ops`.

## Risks and test signals
The code assumes platform data and frontend pointers are valid. `reg_index` is global, not part of per-device state. Unsupported chip IDs fail init with `-EINVAL`. Because chip documentation is limited, tuning constants and PT3 assumptions are high-risk. Tests should cover both known ID rows, init failure on unknown ID, LPF enabled/disabled paths, fast-search wait handling, fractional calculation around band edges, sleep/wakeup register bits, and I2C short-transfer handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/qm1d1c0042.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/qm1d1c0042.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/qm1d1c0042.h

## Purpose
`qm1d1c0042.h` defines platform configuration for the Sharp QM1D1C0042 8PSK satellite tuner driver.

## Important APIs and types
`struct qm1d1c0042_config` contains the frontend pointer, crystal frequency in kHz, LPF enable flag, fast-search flag, and wait times for LPF, fast-search, and normal-search tuning modes. `QM1D1C0042_CFG_XTAL_DFLT` and `QM1D1C0042_CFG_WAIT_DFLT` are sentinel values for default crystal and default wait behavior.

## Control flow and integration
Parent device code passes this config as I2C client platform data. Probe uses `fe` to install tuner ops and copies config into private state. `.set_config` can later update frontend, LPF/search flags, and waits; the implementation currently warns and ignores attempts to change `xtal_freq`.

## State and persistence
Unlike direct attach headers, the config is copied into `struct qm1d1c0042_state`, and the client stores a pointer to that embedded config for removal. The header itself declares no persistent storage.

## Dependencies
The only include is `<media/dvb_frontend.h>`, which provides the frontend type and associated kernel media definitions.

## Risks and test signals
The comment says `xtal_freq` is currently ignored, so callers may believe they configured a crystal that the implementation will not use. A valid `fe` pointer is mandatory. Test signals include default sentinel handling, non-default wait values, ignored xtal warning behavior, and compile checks for I2C client users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/qm1d1c0042.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/qt1010.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/qt1010.c

## Purpose
`qt1010.c` is a DVB tuner driver for the Quantek QT1010 silicon tuner. It identifies the tuner, performs an opaque but documented register-measurement initialization sequence, calculates tuning bytes from the requested RF frequency, and exposes basic DVB tuner operations.

## Important APIs, types, and functions
The private state type is declared in `qt1010_priv.h` as `struct qt1010_priv`. This file implements `qt1010_readreg()`, `qt1010_writereg()`, `qt1010_set_params()`, `qt1010_init_meas1()`, `qt1010_init_meas2()`, `qt1010_init()`, `qt1010_release()`, `qt1010_get_frequency()`, `qt1010_get_if_frequency()`, and `qt1010_attach()`. Register scripts use `qt1010_i2c_oper_t` entries with operations `QT1010_WR`, `QT1010_RD`, and `QT1010_M1`.

## Control flow
Attach allocates private state, opens the frontend I2C gate if available, reads register `0x29`, and accepts only ID `0x39`. It then installs `qt1010_tuner_ops` and stores private state. Init opens the I2C gate, runs a fixed initialization script, performs measurement subroutines that repeatedly read until values stabilize, caches initial values from registers `0x1f`, `0x20`, and `0x25`, performs additional `qt1010_init_meas2()` sweeps for `0x31` through `0x39`, sets a default frequency if the frontend cache has none, and calls `qt1010_set_params()`.

Tuning calculates a divider from `(requested + QT1010_OFFSET) / QT1010_STEP`, snaps the stored frequency to the 125 kHz step, derives 32 MHz, 4 MHz, 2 MHz, and 125 kHz-scale remainders, patches many entries in a 48-operation register script, and executes it under the I2C gate. Several tuning values remain TODO constants for registers `0x11`, `0x12`, and `0x00`.

## State and persistence
Private state stores the config pointer, adapter, measurement-derived init values for registers `0x1f`, `0x20`, and `0x25`, and the last snapped frequency. There is no explicit sleep implementation, bandwidth cache, or lock-status state. Hardware is reprogrammed by the full tuning script on each set-params call.

## Dependencies and integration points
The driver includes `qt1010.h` and `qt1010_priv.h`, relying on DVB frontend and I2C definitions pulled there. It uses direct attach and exports `qt1010_attach()`. All I2C transfers use the caller-provided adapter and optional frontend I2C gate.

## Risks and test signals
The attach failure path after a bad ID does not close the I2C gate before freeing private state, which can affect shared buses. Init can also return early on error without closing the gate. Several register calculations are TODO placeholders, and many magic values come from reverse-engineered behavior. Test signals include attach ID detection, I2C gate balance on success and failure, init measurement convergence, set-params across frequency bands and edge frequencies, snapped-frequency getter behavior, fixed IF reporting at 36.125 MHz, and disabled-Kconfig stub builds through the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/qt1010.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/qt1010.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/qt1010.h

## Purpose
`qt1010.h` is the public board-facing header for the Quantek QT1010 tuner driver. It defines the minimal hardware config and attach API used by DVB frontend/bridge drivers.

## Important APIs and types
`struct qt1010_config` contains only the 7-bit I2C address. The exported API is `qt1010_attach(struct dvb_frontend *fe, struct i2c_adapter *i2c, struct qt1010_config *cfg)`. The attach declaration is guarded by `IS_REACHABLE(CONFIG_MEDIA_TUNER_QT1010)`, with a warning stub that returns `NULL` when the driver is disabled.

## Control flow and integration
Board drivers include this header and call attach with a frontend, adapter, and persistent config. The implementation then probes register `0x29`, installs tuner ops, and stores a pointer to the config. No other policy is exposed through the header; frequency range, step, offset, and IF behavior live in the private header and `.c` implementation.

## State and persistence
The config pointer is retained by `struct qt1010_priv`, so callers must keep it valid for the tuner lifetime. The header declares no mutable global or per-device state.

## Dependencies
The header depends on `<media/dvb_frontend.h>`, which provides `struct dvb_frontend` and associated media constants. It also references `struct i2c_adapter` through the attach signature.

## Risks and test signals
The config surface is intentionally small, so board-specific quirks cannot be described without code changes. Tests should include enabled/disabled Kconfig builds, static checks that board configs are long-lived, and attach failure handling when the expected chip ID is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/qt1010.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/qt1010_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/qt1010_priv.h

## Purpose
`qt1010_priv.h` holds private constants, reverse-engineered register notes, operation codes, and private state declarations for the QT1010 driver. It is not a board-facing API.

## Important APIs and types
The header documents the apparent meaning of registers `0x00` through `0x2f`, including known frequency-scale registers and operation/measurement registers. It defines `QT1010_STEP` as 125 kHz, `QT1010_MIN_FREQ` as 48 MHz, `QT1010_MAX_FREQ` as 860 MHz, and `QT1010_OFFSET` as 1246 MHz. Operation constants are `QT1010_WR`, `QT1010_RD`, and `QT1010_M1`. `qt1010_i2c_oper_t` stores one scripted operation as `{ oper, reg, val }`. `struct qt1010_priv` stores config and I2C pointers, measured init values, and the cached tuned frequency.

## Control flow and integration
The `.c` file uses these constants in attach, init, and tuning. The frequency limits and step feed `dvb_tuner_ops.info`. The offset and step define PLL divider math in `qt1010_set_params()`. The operation type drives fixed init/tuning scripts and measurement helper dispatch.

## State and persistence
The private state fields `reg1f_init_val`, `reg20_init_val`, and `reg25_init_val` persist measurement-derived calibration values from init and are later reused in tuning register calculations. `frequency` stores the snapped RF frequency returned by `.get_frequency`.

## Dependencies
This header depends on `qt1010.h` for `struct qt1010_config` and on media/kernel unit macros such as `kHz` and `MHz` available through the included media headers.

## Risks and test signals
The register map is explicitly uncertain, with several comments marked unknown. Since this private header encodes frequency limits and offset math, mistakes propagate directly to tuning. Tests should validate that operation scripts do not exceed known register bounds, cached measurement fields are initialized before tuning, and frequency range/step metadata matches frontend expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/qt1010_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/r820t.c -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/r820t.c

## Purpose
`r820t.c` implements the Rafael Micro R820T/R620D/R828-family silicon tuner driver. It supports digital and analog TV tuning, standard-specific IF/filter setup, PLL programming, mux/band selection, optional IMR calibration, standby, signal-strength approximation, and shared hybrid tuner instances.

## Important APIs, types, and functions
Private state is `struct r820t_priv`, which stores hybrid list linkage, config pointer, `tuner_i2c_props`, mutex, register shadow, I2C buffer, crystal-cap selection, PLL/internal IF data, filter calibration code, IMR calibration status/data, lock/init flags, and cached standard/mode/bandwidth. `struct r820t_freq_range` describes mux/filter settings per frequency range, and `struct r820t_sect_type` stores IMR search points.

Public integration is `r820t_attach()` and `r820t_tuner_ops`. Major helpers include `shadow_store()`, `r820t_write()`, `r820t_read()`, `r820t_write_reg_mask()`, `r820t_set_mux()`, `r820t_set_pll()`, `r820t_sysfreq_sel()`, `r820t_set_tv_standard()`, `generic_set_freq()`, `r820t_standby()`, `r820t_xtal_check()`, `r820t_imr_prepare()`, the IMR search helpers (`r820t_multi_read()`, `r820t_imr_cross()`, `r820t_compre_step()`, `r820t_iq_tree()`, `r820t_section()`, `r820t_iq()`, `r820t_f_imr()`, `r820t_imr()`), `r820t_imr_callibrate()`, `r820t_init()`, `r820t_sleep()`, `r820t_set_analog_freq()`, `r820t_set_params()`, `r820t_signal()`, and `r820t_get_if_frequency()`.

## Control flow
Attach uses `hybrid_tuner_request_state()` under `r820t_list_mutex`, sets config and per-device mutex for new instances, opens the frontend I2C gate, reads five bytes as a presence check, calls `r820t_sleep()` for standby, closes the gate, installs ops, and returns the frontend. Init locks the instance, opens the gate, runs `r820t_imr_callibrate()` once unless already initialized, then writes the initial register array. Sleep writes a standby register sequence and forces future standard calibration by setting `priv->type = -1`.

Digital `.set_params` derives bandwidth in MHz and calls `generic_set_freq()` with `V4L2_TUNER_DIGITAL_TV`; analog `.set_analog_params` converts V4L2 analog frequency units and chooses 6 or 8 MHz bandwidth. `generic_set_freq()` selects TV-standard settings, computes LO as RF plus internal IF except SECAM-LC analog, sets mux, locks PLL, then applies system-frequency AGC/LNA/mixer parameters. IF and filter setup are recalibrated only when tuner type, analog standard, delivery system, or bandwidth changes.

PLL setup converts frequency to kHz, selects VCO divider, reads fine-tune status, writes integer and sigma-delta fractional values with boundary-spur avoidance, checks lock twice, and updates `has_lock`. IMR calibration detects crystal capacitance for non-R820T-like chips, optionally skips on `no_imr_cal`, prepares calibration registers, and searches five IMR memory regions using measured ADC values.

## State and persistence
The register shadow starts at hardware register 5 and is updated before writes. Cached `type`, `std`, `delsys`, and `bw` avoid unnecessary filter recalibration. `int_freq` is returned by `.get_if_frequency`; `has_lock` controls signal-strength reporting. IMR results persist in `imr_data` for later mux setup. Shared-instance lifetime is controlled by hybrid tuner helpers.

## Dependencies and integration points
The driver depends on V4L2, mutex/slab/bitrev kernel APIs, `tuner-i2c.h`, and `r820t.h`. Reads reverse bit order with `bitrev8()`. It uses frontend I2C gate callbacks in public ops and exports `r820t_attach()`. Module parameters `debug` and `no_imr_cal` affect diagnostics and calibration behavior.

## Risks and test signals
The attach path calls `r820t_sleep()` while the global list mutex is held; that function also locks the per-instance mutex and toggles the I2C gate, so error paths and lock ordering deserve attention. `shadow_store()` updates cache before confirming I2C success, which can desynchronize software state after failed writes. Several comments preserve original-driver quirks and possible mask mistakes. Signal strength is a rough inverse-gain estimate, not calibrated RSSI. Test signals include attach/probe failure cleanup, shared-instance release, init with and without IMR calibration, PLL lock/failure cases, all supported delivery systems and analog standards, bandwidth-change recalibration, max I2C message chunking, bit-reversed reads, standby/resume, IF frequency reporting, and signal-strength behavior when locked versus unlocked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/r820t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/r820t.h -->
# sources/distributed-fs/ceph-client/drivers/media/tuners/r820t.h

## Purpose
`r820t.h` is the public configuration and attach header for the Rafael Micro R820T/R620D/R828-family tuner driver.

## Important APIs and types
`enum r820t_chip` identifies supported chip variants: `CHIP_R820T`, `CHIP_R620D`, `CHIP_R828D`, `CHIP_R828`, `CHIP_R828S`, and `CHIP_R820C`. `struct r820t_config` provides the I2C address, crystal frequency, chip variant, maximum I2C message length, and booleans for diplexer and predetect behavior. `r820t_attach(struct dvb_frontend *fe, struct i2c_adapter *i2c, const struct r820t_config *cfg)` is the public attach API, with a disabled-driver stub that logs and returns `NULL`.

## Control flow and integration
Board drivers provide a persistent `const struct r820t_config` and call attach during frontend setup. The implementation uses `i2c_addr` for hybrid instance identity, `xtal` for PLL and crystal-cap calibration, `rafael_chip` to select chip-specific behavior, `max_i2c_msg_len` to split writes, and the diplexer/predetect flags during standard-specific setup.

## State and persistence
The implementation stores the config pointer directly in private state, so the config must remain valid for the frontend lifetime. No mutable state is declared in the header.

## Dependencies
The header depends on `<media/dvb_frontend.h>` and uses kernel bool/integer types. It references `struct i2c_adapter` in the attach signature and uses `IS_REACHABLE(CONFIG_MEDIA_TUNER_R820T)`.

## Risks and test signals
`max_i2c_msg_len` must be large enough for at least a register byte plus one data byte; invalid values can break write chunking. Incorrect chip variant or crystal frequency changes PLL and calibration behavior. Tests should cover Kconfig enabled/disabled builds, each known chip enum used by board drivers, config lifetime, max-message splitting, and diplexer/predetect board options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/tuners/r820t.h -->
