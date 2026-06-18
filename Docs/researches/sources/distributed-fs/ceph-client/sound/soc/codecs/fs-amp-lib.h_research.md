# sources/distributed-fs/ceph-client/sound/soc/codecs/fs-amp-lib.h

## Purpose

This header defines the FourSemi amplifier firmware binary layout, command encodings, parsed scene structures, and the public firmware-load API used by amplifier codec drivers.

## Important APIs, types, and functions

The public API is `fs_amp_load_firmware(struct fs_amp_lib *amp_lib, const char *name)`. Important types are packed firmware structs `fs_fwm_header`, `fs_fwm_table`, `fs_fwm_index`, `fs_scene_index`, `fs_reg_table`, `fs_file_table`, `fs_cmd_pkg`, `fs_reg_val`, and `fs_reg_bits`; runtime structs `fs_i2s_srate`, `fs_pll_div`, `fs_amp_scene`, and `fs_amp_lib`; enum `fs_index_type`; and command constants `FS_CMD_DELAY`, `FS_CMD_BURST`, and `FS_CMD_UPDATE`.

## Control flow

There is no runtime control flow in the header. The binary layout controls how `fs-amp-lib.c` walks firmware tables and how `fs210x.c` interprets register command packages.

## State and persistence behavior

`struct fs_amp_lib` is the shared persistent parse result: it stores the firmware header pointer, table pointers by index, allocated scene array, owning device, scene count, and expected device ID. Packed structs intentionally mirror on-disk firmware and must not gain padding.

## Dependencies and integration points

The header is shared by `fs-amp-lib.c` and `fs210x.c`. It assumes ALSA control types are visible for `FS_SOC_ENUM_EXT` users and kernel integer typedefs are available from including files.

## Risks and test signals

Risks include ABI breakage if packed structs change, command package ambiguity because the first byte can be either a register address or special command, and `FS_CMD_BURST` being defined but not implemented by the current FS210x command executor. Build all FourSemi consumers and validate firmware parsing/writing with known-good images, delay commands, update commands, and unsupported burst commands.
