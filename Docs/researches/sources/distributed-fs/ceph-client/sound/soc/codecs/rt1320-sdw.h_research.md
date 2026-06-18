# sources/distributed-fs/ceph-client/sound/soc/codecs/rt1320-sdw.h

## Purpose
Header for the RT1320/RT1321 SoundWire SDCA driver. It defines device IDs, vendor/DSP address constants, SDCA function/entity/control/channel ids, firmware file names and command addresses, firmware protocol structures, enums for DAI/version/command/power/read-write modes, and the large private state used by `rt1320-sdw.c`.

## APIs, Types, and Functions
Constants identify RT1320 and RT1321 devices, version and power registers, patch/DSP status addresses, function numbers for amp and mic, SDCA entities for PDE/FU/CS/SAPU/PPU blocks, controls for sample rate, power state, mute, volume, protection, posture, and function status, and sample-rate indexes. Firmware structures include `struct rt1320_datafixpoint`, packed `FwPara_Get_HwSwGain`, and `struct rt1320_paramcmd`. Enums define AIF ids, version ids, firmware command ids, DSP power states, and data read/write modes. `struct rt1320_sdw_priv` stores all runtime state for component, regmaps, slave, initialization, versioning, controls, calibration, firmware flags, work, and BRA transfer state.

## Control Flow
No code executes in the header. The C file uses these definitions to select chip-specific presets and firmware paths, build SDCA control addresses, issue firmware parameter commands, configure DAI ids, gate calibration by DSP power state, and manage runtime state across attach/resume/control operations.

## State and Persistence
The header defines in-memory state only. Fields such as `r0_l_reg`, `r0_r_reg`, `temp_*_calib`, `fw_load_done`, `rae_update_done`, and `cali_done` mirror hardware/DSP state but are not persistent across driver reloads except when seeded by firmware properties or reloaded from firmware files.

## Dependencies and Integration
Includes regmap, SoundWire core/type/register headers, ALSA SoC, and the internal SoundWire bus header for `struct sdw_bpt_msg`. It is tightly bound to `rt1320-sdw.c` and firmware assets named by the macros.

## Risks and Test Signals
Risks include dependence on internal SoundWire bus structures, packed firmware-command layout needing ABI compatibility with DSP firmware, file-name macros needing to match installed firmware, and `long long reserved2` making structure layout sensitive to compiler ABI despite packing only being applied to the gain struct. Test signals include compiling across supported architectures, correct command buffer sizes for SET/GET_PARAM, successful firmware request paths, correct SDCA addresses for amp/mic controls, and state restoration after SoundWire reinitialization.
