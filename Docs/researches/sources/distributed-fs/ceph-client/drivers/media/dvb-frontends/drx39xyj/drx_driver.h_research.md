# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drx39xyj/drx_driver.h

## Purpose
`drx_driver.h` is the generic DRX demodulator driver contract shared by the DRX39xyj implementation. It defines board-support I2C/tuner hooks, tuning and modulation enums, control structures, audio/video/OOB configuration payloads, data-access function tables, demod common attributes, stringification helpers, and access macros.

## Important APIs, Types, and Functions
The BSP layer starts with `struct i2c_device_addr`, `IS_I2C_10BIT()`, `drxbsp_i2c_init()`, `drxbsp_i2c_term()`, `drxbsp_i2c_write_read()`, `drxbsp_i2c_error_text()`, and `drx_i2c_error_g`. Tuner integration is modeled by `struct tuner_common`, `struct tuner_ops`, `struct tuner_instance`, and helper prototypes for set/get frequency and default I2C forwarding. DAP configuration defaults include `DRXDAP_SINGLE_MASTER`, `DRXDAP_MAX_WCHUNKSIZE`, and `DRXDAP_MAX_RCHUNKSIZE`.

The header defines the core RF/channel vocabulary: `enum drx_standard`, `drx_substandard`, `drx_bandwidth`, `drx_mirror`, `drx_modulation`, `drx_hierarchy`, `drx_priority`, `drx_coderate`, `drx_guard`, `drx_fft_mode`, `drx_classification`, `drx_interleave_mode`, `drx_carrier_mode`, `drx_frame_mode`, `drx_tps_frame`, `drx_ldpc`, `drx_pilot_mode`, `drxu_code_action`, `drx_lock_status`, `drx_uio`, and OOB/audio enums. Main payload structures include `drxu_code_info`, `drx_mc_version_rec`, `drx_filter_info`, `drx_channel`, `drx_frequency_plan`, `drx_scan_param`, `drxtps_info`, `drx_version`, `drx_cfg_mpeg_output`, `drxi2c_data`, audio status/config structures, `drx_access_func`, `drx_reg_dump`, `drx_common_attr`, and `drx_demod_instance`.

## Control Flow
The header establishes a layered control model. Platform I2C and tuner callbacks feed a generic demod instance. Higher-level code issues configuration through `drx_ctrl()` style access macros such as `DRX_ACCESSMACRO_SET()` and `DRX_ACCESSMACRO_GET()`, passing `struct drx_cfg` payloads for device-specific settings. Scan state in `drx_common_attr` tracks frequency-plan progress, inner scan function, lock requirements, and current channel. Data access is abstracted through function pointers for block and 8/16/32-bit register reads, writes, and read-modify-write operations.

## State and Persistence
The file defines the central persistent-in-memory state shape but does not allocate it. `struct drx_common_attr` tracks microcode file/version policy, clocks, IF/mirror settings, MPEG defaults, open state, scan progress, power mode, tuner ranges/polarities, current/previous/cache standards, bootloader use, capabilities, and product ID. `struct drx_demod_instance` connects I2C address, common attributes, device-specific attributes, and the Linux I2C adapter. This state is runtime only; persistence across module reload or power loss is not provided by the header.

## Dependencies and Integration Points
It depends on Linux kernel types, errno, and I2C. It is included by DRX39xyj public and implementation headers and by the FASI DAP header. The string macros support debug/log reporting, while standard-class macros such as `DRX_ISATVSTD()`, `DRX_ISQAMSTD()`, `DRX_ISVSBSTD()`, and `DRX_ISDVBTSTD()` support mode-specific control flow.

## Risks and Edge Cases
This is a very broad ABI-like header with many raw pointers and callback tables, so initialization order and object lifetime are critical. Several macros assume an external `drx_ctrl()` symbol and can hide failures by writing fallback values. `DRX_ATTR_MICROCODE(d)` references `my_common_attr->microcode`, while the visible common attribute field is `microcode_file`; that mismatch should be checked against the implementation before using the macro. Some comments and spellings are legacy, and generated or vendor-style layouts may not follow normal kernel style. Auto/unknown sentinel values share fixed numeric values across many enums, so casts between unrelated enums can mask invalid state.

## Test Signals
Important coverage includes BSP I2C write/read error mapping, tuner callback operation, microcode upload/verify metadata, channel set/get for DVB-T, ATSC 8VSB, QAM, and analog modes, scan plan progress, power-mode transitions, MPEG/I2S/audio/OOB config payloads, DAP function-table calls for all register widths, string macro output for invalid values, and build coverage for all users of DRX access macros.
