# sources/distributed-fs/ceph-client/sound/ppc/tumbler.c

## Purpose
`tumbler.c` implements the low-level PowerMac Tumbler/Snapper mixer and codec support for TAS3001C/TAS3004 based machines. It programs codec registers over the Keywest I2C adapter, exposes ALSA mixer controls, manages audio GPIOs for reset/mute/jack detect, handles automatic mute and optional automatic DRC changes, and restores codec/GPIO state across suspend and resume.

## Important APIs, Types, And Functions
The key private state is `struct pmac_tumbler`, which stores `pmac_keywest` I2C state, GPIO descriptors, IRQ numbers, master volumes/switches, TAS mono/mix volumes, DRC range, capture source, reset style, and Snapper analog control state. `snd_pmac_tumbler_init()` is the exported entry point used by the PowerMac core. Important helpers include `send_init_client()`, `tumbler_init_client()`, `snapper_init_client()`, `tumbler_set_master_volume()`, `tumbler_set_drc()`, `snapper_set_drc()`, `tumbler_set_mono_volume()`, `snapper_set_mix_vol()`, `snapper_set_capture_source()`, `tumbler_find_device()`, `tumbler_reset_audio()`, `tumbler_suspend()`, and `tumbler_resume()`.

## Control Flow
Initialization allocates `pmac_tumbler`, records the cleanup hook, discovers Open Firmware audio GPIOs and jack IRQs, resets the codec through either the normal reset GPIO or the anded-reset mute GPIO sequence, locates the TAS codec node and I2C address, initializes Keywest I2C, registers model-specific mixer controls, initializes DRC defaults, installs PM callbacks, initializes the device-change work item, and optionally requests jack-detect IRQs. Mixer `put` callbacks validate ALSA values, update shadow state, and write TAS registers. Jack IRQs schedule `device_change_handler()`, which reads headphone/line-out GPIOs and writes mute GPIOs before reapplying master volume and optional DRC.

## State And Persistence
Runtime state is persisted in `chip->mixer_data`, ALSA control objects, static `device_change`/`device_change_chip`, IRQ registrations, and the TAS codec/GPIO hardware. The driver keeps shadow copies of volumes, switches, DRC, Snapper mixer values, and `acs` so resume can reinitialize the codec and replay every user-visible control. Suspend saves master volume/switches, mutes output, optionally powers down Snapper analog control, disables jack IRQs, and asserts reset/mute GPIOs.

## Dependencies And Integration Points
This file integrates with the PowerMac ALSA core (`struct snd_pmac`), Keywest I2C helpers, Open Firmware GPIO and IRQ discovery, `pmac_call_feature()` GPIO access, ALSA control APIs, optional `PMAC_SUPPORT_AUTOMUTE`, optional `CONFIG_SND_POWERMAC_AUTO_DRC`, and volume tables from `tumbler_volume.h`. It depends on machine quirks such as `PowerMac3,4`, `has-anded-reset`, `layout-id`, and Open Firmware `platform-do-*` GPIO scripts.

## Risks And Edge Cases
GPIO polarity discovery relies on firmware properties and script heuristics, so wrong polarity can invert mute or jack detection. Several init error paths return after partially allocated controls or I2C state, relying on higher-level card cleanup. The global device-change work pointer assumes a single active PowerMac mixer. I2C register writes are retried only during codec init, while control writes surface as `-EINVAL`. Auto-mute suppresses manual mute control changes when enabled, and anded-reset machines need extra sleeps to avoid audible or electrical glitches.

## Test Signals
Useful tests include boot/probe on TAS3001C and TAS3004 machines, ALSA mixer get/put validation for master, bass, treble, PCM, Snapper mix, DRC, capture source, and mute controls; jack insertion/removal with notification checks; suspend/resume replay of all controls; I2C failure injection; Open Firmware GPIO polarity variants; and regression testing on anded-reset and line-out-equipped systems.
