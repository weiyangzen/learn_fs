# sources/distributed-fs/ceph-client/sound/soc/codecs/aw88395/aw88395_data_type.h

## Purpose
`aw88395_data_type.h` defines the on-disk Awinic ACF configuration schema and in-memory profile descriptors used by AW88395 and reused by AW88399. It is the contract between firmware files and the runtime parser.

## Important APIs And Types
The header defines string-size limits, `ACF_FILE_ID`, ACF header versions (`AW88395_CFG_HDR_VER` and `AW88395_CFG_HDR_VER_V1`), device descriptor types, section types, profile data slots, and named profile IDs. `struct aw_cfg_hdr` describes the ACF header and DDT table location. `struct aw_cfg_dde` and `struct aw_cfg_dde_v1` describe per-device/per-profile data entries, with v1 adding profile strings and chip ID. `struct aw_sec_data_desc`, `struct aw_prof_desc`, `struct aw_all_prof_info`, and `struct aw_prof_info` model parsed register, DSP config, DSP firmware, profile names, and profile counts.

## Control Flow And State
The parser first validates `aw_cfg_hdr`, then chooses old or v1 descriptor layout based on `hdr_version`. Matching uses either exact bus/address/device descriptors or default channel/chip descriptors. Parsed profiles store pointers into the copied firmware container rather than duplicating section data, so the ACF container lifetime must exceed all runtime use.

## Dependencies And Integration Points
The structures use fixed-width Linux types (`u8`, `u16`, `u32`) and are consumed by `aw88395_lib.c`, `aw88395_device.c`, and `aw88399.c`. Firmware-generation tools must match these layouts, endianness expectations, CRC fields, profile IDs, and section data types.

## Risks And Test Signals
The file is a binary ABI: changing field order or sizes would break existing ACF files. Parser robustness depends on validating offsets, lengths, and CRCs before dereferencing. Test signals include rejection of wrong `ACF_FILE_ID`, unsupported header versions, bad CRC8, overflowed data offsets, and valid profile counts/names after loading real firmware.
