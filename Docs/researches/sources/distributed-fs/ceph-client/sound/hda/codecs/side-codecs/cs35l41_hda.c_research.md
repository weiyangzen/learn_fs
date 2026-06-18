# sources/distributed-fs/ceph-client/sound/hda/codecs/side-codecs/cs35l41_hda.c

## Purpose
`cs35l41_hda.c` is the common Cirrus Logic CS35L41 smart-amplifier side-codec driver for HD-audio systems. It handles ACPI/property discovery, reset/OTP/errata setup, boost and GPIO configuration, speaker-ID and calibration data, DSP firmware loading, ALSA controls, HDA component binding, playback hooks, IRQ recovery, and runtime/system power management.

## APIs, Types, and Functions
Exported APIs are `cs35l41_hda_probe()`, `cs35l41_hda_remove()`, `cs35l41_hda_pm_ops`, `cs35l41_get_speaker_id()`, and `cs35l41_hda_parse_acpi()`. Major internal areas include firmware filename search (`cs35l41_request_firmware_*()`), tuning params, calibration, DSP init/shutdown, playback hooks, channel mapping, ID verification, suspend/resume, ALSA controls, ACPI DSM mute notifications, component bind/unbind, IRQ handlers, property application, and ACPI reading.

## Control Flow
Probe allocates `struct cs35l41_hda`, reads ACPI or extra DSD properties, handles reset GPIO, software-resets the device, waits for OTP boot, verifies chip ID/revision, applies errata and OTP unpack, reads EFI calibration, mutes, initializes work/mutex/runtime PM, applies boost/GPIO/channel properties, then registers as an HDA component. Bind connects to the parent HDA codec, sets firmware type, optionally autoloads DSP firmware, creates ALSA controls, installs pre/main/post playback hooks and ACPI notification handling, and creates a device link. Playback open resumes runtime PM; prepare configures mixer and starts amp/DSP; post-prepare globally enables and unmutes; cleanup pauses/mutes/releases errors; close schedules deferred firmware load if needed and autosuspends.

## State and Persistence Behavior
Persistent state is `struct cs35l41_hda`: regmap, GPIOs, hardware config, codec/component linkage, ACPI subsystem ID, firmware type, speaker ID, DSP state, work flags, playback flag, mute override, tuning gain, calibration data, IRQ errors, and runtime PM state. Regmap cache is marked dirty around reset/hibernate and synced on resume. Firmware request/load state is protected by `fw_mutex` and deferred work.

## Dependencies and Integration Points
Dependencies include ALSA HDA/generic/component glue, ASoC CS35L41 library, CS DSP firmware framework, Cirrus amp calibration library, ACPI/EFI, GPIO, regmap IRQ, runtime PM, SPI/I2C bus wrappers, and firmware files under `cirrus/cs35l41-*.wmfw` and `.bin`.

## Risks
Firmware filename fallback order, ACPI property indexing, reset sharing, SPI speed gating, and runtime PM all affect whether speakers work. Loading/unloading firmware during playback is blocked but deferred work races must stay locked. External-boost systems without VSPK switch do not support suspend. IRQ setup failures leave amp errors unrecoverable without reboot.

## Test Signals
Validate probe on I2C/SPI variants, property parsing for multi-amp arrays, speaker-ID selection, firmware autostart on/off, fallback firmware names, tuning parameter validation, calibration application, ALSA DSP controls, ACPI mute notifications, playback hook ordering, runtime/system suspend/resume, IRQ fault release, and cleanup on every probe error path.
