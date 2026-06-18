<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drxk_hard.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drxk_hard.h

## Purpose
`drxk_hard.h` is the private hardware-state header for `drxk_hard.c`. It collects DRX-K version constants, power/lock/status enumerations, modulation and DVB-T/QAM configuration enums, AGC/pre-SAW helper structs, SCU command containers, the full `struct drxk_state`, and lock-status constants used by the DRX-K driver implementation.

## Important APIs, Types, and Functions
This header does not export callable functions; its main API is data shape. Important definitions include `DRXK_VERSION_MAJOR/MINOR/PATCH`, host-interface timing constants, `DRXK_MAX_RETRIES`, DRX JTAG IDs, `DRX_UNKNOWN`, `DRX_AUTO`, SCU result codes, MPEG bitrate constants, and IQM adjustment constants.

Core enums are `enum operation_mode` (`OM_NONE`, DVB-C Annex A/B/C QAM, DVB-T), `enum drx_power_mode`, `enum agc_ctrl_mode`, `enum e_drxk_state`, `enum e_drxk_coef_array_index`, `enum e_drxk_sif_attenuation`, `enum e_drxk_constellation`, `enum e_drxk_interleave_mode`, spin revision values, `enum drxk_cfg_dvbt_sqi_speed`, `enum drx_fftmode_t`, `enum drxmpeg_str_width_t`, and `enum drx_qam_lock_range_t`.

Configuration structs include `struct drxk_cfg_dvbt_echo_thres_t`, `struct s_cfg_agc`, `struct s_cfg_pre_saw`, and `struct drxk_ofdm_sc_cmd_t`. `struct drxk_state` embeds the `struct dvb_frontend`, cached DVB properties, device and I2C handles, mutex, chip capability flags, HI timing, current mode/state, AGC presets for VSB/ATV/QAM/DVB-T, MPEG/TS output flags, QAM and DVB-T tuning state, GPIO configuration, microcode/firmware state, bridge and board options from `struct drxk_config`, frontend status, and QAM command ABI tracking.

## Control Flow
The header shapes control flow by providing the state machine values consumed by `drxk_hard.c`. Initialization moves `m_drxk_state` through uninitialized, stopped, started, powered down, or no-device states. `m_operation_mode` selects QAM versus DVB-T paths. `m_current_power_mode` controls transitions through power-up, OFDM-down, core-down, PLL-down, or oscillator-only modes. Lock constants `NEVER_LOCK`, `NOT_LOCKED`, `DEMOD_LOCK`, `FEC_LOCK`, and `MPEG_LOCK` normalize hardware-specific lock readings for DVB callbacks.

## State and Persistence
`struct drxk_state` is allocated per attached frontend and is the driver's in-memory persistence boundary. It keeps board configuration, runtime hardware state mirrors, statistics status, and firmware pointer for the life of the frontend. The header itself stores no data, but changing fields or defaults affects every mode setup and statistics path in `drxk_hard.c`.

## Dependencies and Integration Points
The header includes `drxk_map.h` and relies on kernel/DVB types made available by the C file and public `drxk.h`. It is private to the DRX-K implementation, with `struct drxk_state` matching register definitions and command helpers in `drxk_hard.c`.

## Risks and Edge Cases
The large `struct drxk_state` mixes board configuration, hardware capability, cached frontend properties, firmware, counters, and mode state; field initialization order is important. Several comments note board-specific defaults that likely belong in `struct drxk_config`, so using the header values across different hardware designs can be fragile. Enum sentinel values use `DRX_UNKNOWN` and `DRX_AUTO` aliases, and code must not treat them as normal low-range enum entries.

## Test Signals
Header-level validation is mostly compile and runtime-coverage based: `drxk_hard.c` should build without mismatched fields, all configured board options should land in expected `drxk_state` fields, state transitions should reject uninitialized/no-device states, and DVB-C/DVB-T capability detection should populate delivery-system support consistently with the capability flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drxk_hard.h -->
