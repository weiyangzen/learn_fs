# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drx39xyj/drxj.h

## Purpose

`drxj.h` is the DRX-J-specific private interface for the Micronas/Trident DRX39xxJ DVB frontend driver. It does not implement algorithms itself; it defines the DRX-J control/configuration IDs, configuration payload types, persistent per-demodulator extension state, lock/power constants, carrier-frequency offsets, and small access macros consumed by `drxj.c`.

The header sits below the generic DRX driver model from `drx_driver.h` and above the register-access layer from `drx_dap_fasi.h`. Its definitions let the implementation cache hardware state in `struct drxj_data`, translate DVB frontend operations into DRX-J mode/channel programming, and exchange compact command packets with the SCU microcontroller.

## Important APIs, Types, and Constants

- Include guard and dependencies: includes `drx_driver.h` for common DRX enums/attributes, DVB-facing control structures, `struct drx_demod_instance`, `struct drx_common_attr`, audio data, UIO modes, standards, bandwidths, mirrors, lock states, and power modes; includes `drx_dap_fasi.h` for DRX-J DAP/FASI addressing configuration. A preprocessor guard rejects the unsupported combination of multi-master DAP with short-only addresses.
- Lock and power aliases: `DRXJ_DEMOD_LOCK`, `DRXJ_OOB_AGC_LOCK`, and `DRXJ_OOB_SYNC_LOCK` map generic intermediate lock states to DRX-J demod/OOB meanings. `DRXJ_POWER_DOWN_MAIN_PATH`, `DRXJ_POWER_DOWN_CORE`, and `DRXJ_POWER_DOWN_PLL` extend the shared power-mode enum with DRX-J-specific sleep depths used by `ctrl_power_mode()`.
- `struct drxjscu_cmd`: SCU command descriptor containing command ID, parameter/result lengths, and caller-owned `u16` parameter/result buffers. `drxj.c` passes it to `scu_command()`, which writes SCU RAM parameter registers, posts the command, waits for `DRX_SCU_READY`, reads result registers, and maps SCU errors to `-EINVAL`/`-EIO`.
- `enum drxj_cfg_type`: DRX-J device-specific configuration namespace starting at `DRXJ_CTRL_CFG_BASE` (`0x1000`). It names configuration channels for RF/IF/internal AGC, pre-SAW, AFE gain, symbol-clock offset, accumulated Reed-Solomon errors, OOB state, smart antenna, VSB misc, packet-error reset, ATV output/misc/equalizer/AGC status, MPEG output misc, hardware config, and OOB LO power.
- AGC/AFE/pre-SAW payloads: `enum drxj_agc_ctrl_mode`, `struct drxj_cfg_agc`, `struct drxj_cfg_pre_saw`, and `struct drxj_cfg_afe_gain` describe per-standard gain behavior. `set_agc_rf()`, `set_agc_if()`, `ctrl_set_cfg_pre_saw()`, and `ctrl_set_cfg_afe_gain()` validate standards/ranges, program active hardware registers when applicable, and cache settings in `struct drxj_data`.
- Signal/status payloads: `struct drxj_agc_status`, `struct drxjrs_errors`, `struct drxj_cfg_vsb_misc`, and `struct drxj_cfg_oob_misc` carry AGC readings, Reed-Solomon counters, VSB symbol error data, and OOB lock/state flags.
- MPEG and hardware configuration: `enum drxj_mpeg_start_width`, `enum drxj_mpeg_output_clock_rate`, `struct drxj_cfg_mpeg_output_misc`, `enum drxj_xtal_freq`, `enum drxji2c_speed`, and `struct drxj_cfg_hw_cfg` represent DRX-J-specific MPEG clock/start-width and hardware identification choices. The implementation also uses the generic `struct drx_cfg_mpeg_output` from `drx_driver.h` for the main MPEG pin/clock programming path.
- ATV/OOB support types: `struct drxj_cfg_atv_misc`, OOB state constants (`DRXJ_OOB_STATE_*`), `enum drxj_cfg_oob_lo_power`, `struct drxj_cfg_atv_equ_coef`, `enum drxj_coef_array_index`, `enum drxjsif_attenuation`, `struct drxj_cfg_atv_output`, and `struct drxj_cfg_atv_agc_status` describe analog TV equalizer/filter/output/AGC configuration and OOB low-power behavior.
- `struct drxj_data`: the main persistent DRX-J extension state stored in `demod->my_ext_attr`. It contains detected capabilities, current standard/channel settings, quality measurement periods, host-interface config, UIO pin modes, IQM frequency-shift state, ATV shadow registers and changed flags, QAM/VSB/ATV AGC/pre-SAW/PGA caches, version storage, smart antenna flags, OOB tracking/filter/power settings, MPEG misc settings, pin-safe restore values, current symbol rate, OOB pre-SAW/LO power, and embedded audio state.
- Access/utility macros: `DRXJ_ATTR_BTSC_DETECT(d)` projects the BTSC-detect flag out of `struct drxj_data::aud_data`. Carrier offset constants convert listed analog picture/sound carriers to center frequencies when no tuner module handles the offset. `DRXJ_TYPE_ID` identifies the device family, and `DRXJ_STR_OOB_LOCKSTATUS(x)` renders generic/OOB lock states to strings.

## Control Flow and Integration

The header is pulled directly into `drxj.c`, where `drx39xxj_attach()` allocates a DVB frontend state, clones `drxj_default_demod_g`, `drxj_default_comm_attr_g`, and `drxj_data_g`, installs the clone as `demod->my_ext_attr`, sets firmware and IF defaults, and calls `drxj_open()`. The resulting `dvb_frontend_ops` expose ATSC and DVB-C Annex B tuning, sleep/init, I2C gate control, status/stat reads, LNA control, and release.

Initialization flows through `drxj_open()`: power up, read device capabilities into `struct drxj_data`, soft-reset hardware, configure analog/IQM/OOB/host-interface blocks, disable MPEG output while initializing, stop/upload/verify firmware if present, start SCU execution, set scan lock defaults, call `drxj_reset_mode()` to repopulate AGC/pre-SAW/PGA defaults from detected LNA capability, initialize smart antenna/OOB state, refresh audio defaults, mark the instance opened, and disable LNA.

Tuning flows from `drx39xxj_set_frontend()` to tuner setup, then `ctrl_set_standard()` and `ctrl_set_channel()`. Those lower-level paths consult and update `struct drxj_data` fields such as `standard`, `constellation`, `frequency`, `curr_bandwidth`, `mirror`, `curr_symbol_rate`, AGC/pre-SAW caches, IQM offsets, and MPEG configuration. Status reads call `ctrl_lock_status()` and `ctrl_sig_quality()`, which use the lock constants and measurement-period fields defined/cached through this header.

Power management flows through `ctrl_power_mode()`, using the DRX-J intermediate power constants from this header. On power-up it restores mode defaults via `drxj_reset_mode()`; on power-down it dispatches to QAM/VSB/ATV power-down helpers based on `ext_attr->standard`, clears the current standard, programs SIO power registers, and may prepare host-interface sleep settings.

The generic `struct drx_cfg` and access macros live in `drx_driver.h`; `drxj.h` supplies the DRX-J config IDs and payload shapes. In this source snapshot, most config operations are wired as local helpers in `drxj.c` rather than through an exported generic `drx_ctrl()` dispatcher.

## State and Persistence Behavior

`struct drxj_data` is per-frontend runtime state, not on-disk persistence. Defaults live in the static `drxj_data_g` initializer in `drxj.c`; attach clones it with `kmemdup()`, and release frees it. Cached fields persist across normal control calls for the lifetime of the attached frontend and are reinitialized selectively by `drxj_open()`, `drxj_reset_mode()`, standard changes, channel changes, and power transitions.

Several fields deliberately shadow hardware register state so settings survive inactive-standard configuration and can be applied when the standard becomes active. Examples include QAM/VSB/ATV AGC structures, pre-SAW references, PGA gains, ATV equalizer coefficients and output flags, MPEG misc flags, UIO modes, OOB tracking filter values, and pin-safe restore registers. Setters often write hardware only when the requested standard matches the active standard, then cache the requested state regardless.

Quality/statistics state includes measurement periods and accumulated packet-error reset markers. The packet-error accumulator path in `drxj.c` uses static local counters plus `ext_attr->reset_pkt_err_acc`/`pkt_err_acc_start`; this means careful reset behavior matters when retuning or when multiple frontend instances exist.

Firmware is not defined by this header, but the state it supports is initialized during open: `drxj_open()` requests `DRX39XX_MAIN_FIRMWARE`, uploads/verifies microcode via DAP/FASI helpers, starts the SCU, stamps driver version words into SCU RAM, and refreshes audio state.

## Dependencies

- Kernel/DVB APIs used by consumers: `struct dvb_frontend`, DVBv5 property/stat fields, `request_firmware()`, `kmemdup()`, `kfree()`, sleep/timing helpers, and kernel integer/bool types.
- DRX common layer: `drx_driver.h` provides common standards, modulation, lock status, power, UIO, MPEG, audio, firmware block, and demod instance definitions.
- Register-access layer: `drx_dap_fasi.h`, `drxj_map.h`, and the DAP/FASI helpers in `drxj.c` provide register addresses/masks and I2C read/write/block/atomic access.
- Firmware/microcontroller contract: `struct drxjscu_cmd`, SCU RAM command/parameter registers, and command result codes must match the DRX-J firmware image loaded by the driver.
- Build integration: the surrounding `Makefile`/`Kconfig` compile this as the DRX39xxJ DVB frontend, and `drxj.c` exports `drx39xxj_attach()`.

## Risks and Edge Cases

- The public-looking config payloads depend on caller discipline: many structs carry range comments, but enforcement is uneven and usually in `drxj.c`; invalid standards, unsupported OOB/ATV/LNA capability combinations, or out-of-range values can return `-EINVAL` or silently cache settings until a mode is active.
- `struct drxj_data` is large and order-sensitive because `drxj_data_g` uses positional initialization. Adding, removing, or reordering fields can silently corrupt defaults unless the initializer is updated with equal care.
- The header contains legacy spelling mistakes in field names (`bit_reverse_mpeg_outout`, `disable_te_ihandling`) that are part of the C ABI inside this driver. Renaming them without updating all users will break builds.
- Capability flags (`has_lna`, `has_oob`, `has_ntsc`, `has_btsc`, pin availability) are detected at open and drive later behavior. Incorrect detection can make LNA/UIO/OOB/ATV paths program unsupported pins or reject valid user requests.
- SCU command lengths are small and fixed by switch statements in `scu_command()`. Mismatched `parameter_len`, `result_len`, or NULL buffers can fail with `-EINVAL`/`-EIO`; oversized atomic SCU access is rejected.
- Packet-error accumulation uses static function-local counters in the implementation, which may not be instance-isolated if multiple demods are attached.
- Power transitions clear `ext_attr->standard` and rely on cached configuration to restore mode. Missing cache updates or partial write failures can leave software state and hardware state divergent.
- The compile-time DAP address-mode guard prevents one illegal bus configuration; other bus/address assumptions still depend on the surrounding DAP/FASI definitions.

## Test Signals

- Build coverage: compile the DRX39xxJ frontend with the same Kconfig options, including any `DRXJ_VSB_ONLY` variants, to catch struct initializer drift, enum/type mismatches, and stale field names.
- Attach/open path: verify `drx39xxj_attach()` succeeds, firmware is requested and uploaded/verified, `drxj_open()` marks `is_opened`, detected capability flags are sane, and release frees all cloned state.
- Tuning path: exercise ATSC 8VSB and DVB-C Annex B QAM64/QAM256 through `set_frontend()`, then confirm `read_status()` reaches lock and DVBv5 stat scales/values become available.
- Power/resume path: call sleep/init/resume sequences and confirm `ctrl_power_mode()` restores AGC/pre-SAW/PGA defaults, host-interface wake behavior, MPEG output state, and standard/channel programming.
- Config paths: test RF/IF AGC auto/user/off, pre-SAW, AFE gain clamping, MPEG output options, OOB state/status, smart antenna, and LNA set/reject behavior on devices with and without the relevant capabilities.
- Error handling: inject I2C/DAP failures, missing or corrupt firmware, SCU timeout/error results, unsupported delivery systems, and invalid config ranges; expected outcomes are clean `-EINVAL`/`-EIO` returns without leaked frontend state or stale `is_opened`.
