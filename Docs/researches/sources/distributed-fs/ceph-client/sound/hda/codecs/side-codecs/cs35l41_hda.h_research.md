# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l41_hda.h

## Purpose
`cs35l41_hda.h` defines the public state and function interface for the CS35L41 HD-audio side-codec core used by bus-specific I2C/SPI wrappers and the common HDA component code.

## APIs, Types, and Functions
Important constants are `CS35L41_MAX_ACCEPTABLE_SPI_SPEED_HZ`, `DEFAULT_AMP_GAIN_PCM`, and `DEFAULT_AMP_GAIN_PDM`. Types include packed calibration structures `cs35l41_amp_cal_data` and `cs35l41_amp_efi_data`, speaker-position enum, GPIO-function enum, `enum control_bus`, main `struct cs35l41_hda`, and `enum halo_state`. Declared APIs are `cs35l41_hda_probe()`, `cs35l41_hda_remove()`, `cs35l41_get_speaker_id()`, `cs35l41_hda_parse_acpi()`, and exported PM ops.

## Control Flow
Bus wrappers call `cs35l41_hda_probe()` with device name, instance id, IRQ, regmap, and control bus. The common driver stores runtime state in `struct cs35l41_hda`; remove and PM callbacks consume the same state. The ACPI parse and speaker-ID helpers are exposed for reuse and testing.

## State and Persistence Behavior
`struct cs35l41_hda` persists the device, regmap, reset/chip-select GPIOs, hardware config, parent HDA codec, IRQ/index/channel fields, firmware and DSP state, ACPI data, mute override, bus type, bypass flag, tuning gain, calibration data, and validity flags. This state coordinates firmware work, playback hooks, PM, and component binding.

## Dependencies and Integration Points
The header depends on ACPI, EFI, regulator/GPIO/device APIs, CS35L41 sound definitions, Cirrus amp library, CS DSP firmware headers, and WMFW definitions. It integrates with I2C/SPI side-codec modules and namespace exports from `cs35l41_hda.c`.

## Risks
The main risk is shared-structure drift: adding fields requires correct initialization, locking, cleanup, and PM handling in the implementation. Packed EFI calibration layout must match firmware data exactly. GPIO function enum spelling and values must match ACPI property expectations.

## Test Signals
Compile I2C/SPI wrappers, verify PM ops export, exercise ACPI parser and speaker-ID helper, validate calibration structure size/packing, and run probe/remove suspend/resume tests using both control buses.
